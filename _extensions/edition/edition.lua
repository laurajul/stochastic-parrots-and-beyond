-- Edition shortcode.
--
-- Renders the facts of a course edition from `data/editions.yml`. `_quarto.yml`
-- loads that file through `metadata-files`, so every page sees `editions` and
-- `featured_edition` in its metadata. The shortcode runs at build time. The
-- published site contains plain HTML and fetches nothing at runtime.
--
-- Usage:
--   {{< edition hs2026 date >}}        one field; a missing value renders TBC
--   {{< edition hs2026 facts >}}       the practical-information table
--   {{< edition hs2026 banner >}}      the status notice for one edition
--   {{< edition featured banner >}}    the status notice for the featured edition
--   {{< edition all list >}}           a list of all editions with links
--   {{< edition hs2026 evaluation >}}  the evaluation link (edition page only)
--   {{< edition hs2026 official_url link="Course page" >}}  a field as a link
--
-- A field that is null, empty, or absent renders as "To be confirmed".
-- Never fill a missing value from another edition.

local TBC = 'To be confirmed'

local MONTHS = {
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
}
local WEEKDAYS = { 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' }

local STATUS_LABEL = {
  planned = 'Planned',
  confirmed = 'Confirmed',
  delivered = 'Archive'
}

local PROGRAM_LABEL = {
  proposed = 'Proposed sequence, awaiting instructor approval',
  approved = 'Approved',
  tbc = TBC
}

local REGISTRATION_LABEL = {
  open = 'Open',
  closed = 'Closed',
  upcoming = 'Not yet open'
}

-- Convert a metadata value to a plain string. Return nil for a missing value.
local function str(value)
  if value == nil then
    return nil
  end
  local s = pandoc.utils.stringify(value)
  if s == '' or s == 'null' or s == '~' then
    return nil
  end
  return s
end

local function editions(meta)
  local all = meta['editions']
  if all == nil then
    quarto.log.error('edition shortcode: `editions` is missing. Check metadata-files in _quarto.yml.')
    return {}
  end
  return all
end

local function resolve_id(id, meta)
  if id == 'featured' then
    return str(meta['featured_edition'])
  end
  return id
end

local function edition(id, meta)
  local e = editions(meta)[id]
  if e == nil then
    quarto.log.error('edition shortcode: unknown edition `' .. tostring(id) .. '`.')
  end
  return e
end

-- '2026-11-04' -> 'Wednesday, 4 November 2026'
local function format_date(iso)
  if iso == nil then
    return nil
  end
  local y, m, d = iso:match('^(%d%d%d%d)%-(%d%d)%-(%d%d)')
  if y == nil then
    return iso
  end
  y, m, d = tonumber(y), tonumber(m), tonumber(d)
  -- Noon avoids an off-by-one day from a time-zone shift.
  local t = os.time({ year = y, month = m, day = d, hour = 12 })
  local wday = os.date('*t', t).wday
  return string.format('%s, %d %s %d', WEEKDAYS[wday], d, MONTHS[m], y)
end

-- '2026-10-07T12:00:00+02:00' -> '7 October 2026, 12:00'
local function format_timestamp(iso)
  if iso == nil then
    return nil
  end
  local y, m, d, hh, mm = iso:match('^(%d%d%d%d)%-(%d%d)%-(%d%d)T(%d%d):(%d%d)')
  if y == nil then
    return format_date(iso)
  end
  return string.format('%d %s %d, %s:%s', tonumber(d), MONTHS[tonumber(m)], tonumber(y), hh, mm)
end

local function page_path(id)
  return '/contents/editions/' .. id .. '.qmd'
end

local function text(s)
  return pandoc.Inlines(pandoc.Str(s or TBC))
end

local function link(label, url)
  if url == nil then
    return text(nil)
  end
  return pandoc.Inlines({ pandoc.Link(label, url) })
end

-- Values derived from one or more fields. Each returns a string or nil.
local DERIVED = {
  date = function(e) return format_date(str(e.date)) end,
  time = function(e)
    local s, t = str(e.start), str(e['end'])
    if s == nil or t == nil then return nil end
    return s .. '–' .. t
  end,
  when = function(e)
    local d = format_date(str(e.date))
    local s, t = str(e.start), str(e['end'])
    if d == nil then return nil end
    if s == nil or t == nil then return d end
    return d .. ', ' .. s .. '–' .. t
  end,
  status = function(e) return STATUS_LABEL[str(e.status) or ''] or str(e.status) end,
  capacity = function(e)
    if e.capacity == nil then return nil end
    local lo, hi = str(e.capacity.minimum), str(e.capacity.maximum)
    if lo == nil or hi == nil then return nil end
    return lo .. '–' .. hi .. ' participants'
  end,
  workload = function(e)
    local w = e.workload_hours
    if w == nil then return nil end
    local p, a, f = tonumber(str(w.preparation)), tonumber(str(w.attendance)), tonumber(str(w.follow_up))
    if p == nil or a == nil or f == nil then return nil end
    return string.format('%d hours in total: %d h preparation, %d h attendance, %d h follow-up', p + a + f, p, a, f)
  end,
  credits = function(e)
    local ects = str(e.ects)
    if ects == nil then return nil end
    local s = ects .. ' ECTS'
    local module = str(e.ai_skills_module)
    local hours = e.workload_hours and str(e.workload_hours.attendance)
    if module ~= nil then
      s = s .. '. It may count towards the AI-Skills Focus Area, Module ' .. module
      if hours ~= nil then
        s = s .. ' (' .. hours .. ' hours)'
      end
    end
    return s .. '.'
  end,
  registration = function(e)
    local status = REGISTRATION_LABEL[str(e.registration_status) or '']
    local opens = format_timestamp(str(e.registration_opens))
    local closes = format_timestamp(str(e.registration_deadline))
    if status == nil and opens == nil and closes == nil then return nil end
    local parts = {}
    if status ~= nil then table.insert(parts, status) end
    if opens ~= nil then table.insert(parts, 'opened ' .. opens) end
    if closes ~= nil then table.insert(parts, 'closed ' .. closes) end
    if status == 'Open' or status == 'Not yet open' then
      parts = { status }
      if opens ~= nil then table.insert(parts, 'opens ' .. opens) end
      if closes ~= nil then table.insert(parts, 'closes ' .. closes) end
    end
    return table.concat(parts, '; ')
  end,
  registration_deadline = function(e) return format_timestamp(str(e.registration_deadline)) end,
  registration_opens = function(e) return format_timestamp(str(e.registration_opens)) end,
  assessment_deadline = function(e) return format_date(str(e.assessment_deadline)) end,
  detailed_program = function(e)
    return PROGRAM_LABEL[str(e.detailed_program_status) or ''] or str(e.detailed_program_status)
  end,
  no_show_fee = function(e)
    local fee = str(e.no_show_fee_chf)
    if fee == nil then return nil end
    return 'CHF ' .. fee
  end
}

local function value(e, field)
  if DERIVED[field] ~= nil then
    return DERIVED[field](e)
  end
  local v = e[field]
  if type(v) == 'table' and v.t == nil and #v == 0 then
    -- A map has no single string form.
    quarto.log.warning('edition shortcode: field `' .. field .. '` is a map. Use a derived field.')
    return nil
  end
  return str(v)
end

local function facts_table(id, e)
  local rows = {}
  local function row(label, inlines)
    table.insert(rows, { pandoc.Plain(pandoc.Inlines(pandoc.Strong(label))), pandoc.Plain(inlines) })
  end

  row('Status', text(DERIVED.status(e)))
  row('Date', text(DERIVED.date(e)))
  row('Time', text(DERIVED.time(e)))
  row('Venue', text(str(e.venue)))
  local address = str(e.address)
  local map = str(e.map_url)
  if address ~= nil and map ~= nil then
    local inl = pandoc.Inlines(pandoc.Str(address))
    inl:insert(pandoc.Str(' ('))
    inl:insert(pandoc.Link('directions to the building', map))
    inl:insert(pandoc.Str(')'))
    row('Address', inl)
  else
    row('Address', text(address))
  end
  row('Instructors', text(str(e.instructors)))
  row('Organizer', text(str(e.organizer)))
  local contact = str(e.contact)
  if contact ~= nil then
    row('Course administration', pandoc.Inlines(pandoc.Link(contact, 'mailto:' .. contact)))
  else
    row('Course administration', text(nil))
  end
  row('Audience', text(str(e.eligible_group)))
  row('Capacity', text(DERIVED.capacity(e)))
  row('Fee', text(str(e.fee)))
  row('Credits', text(DERIVED.credits(e)))
  row('Workload', text(DERIVED.workload(e)))
  row('Registration', text(DERIVED.registration(e)))
  row('Official listing', link('University of Basel course page', str(e.official_url)))
  row('Detailed program', text(DERIVED.detailed_program(e)))
  row('Assignment deadline', text(DERIVED.assessment_deadline(e)))

  local header = { pandoc.Plain('Item'), pandoc.Plain('Value') }
  local caption = 'Practical information: ' .. (str(e.label) or id)
  local simple = pandoc.SimpleTable(
    caption,
    { pandoc.AlignLeft, pandoc.AlignLeft },
    { 0.3, 0.7 },
    header,
    rows
  )
  local tbl = pandoc.utils.from_simple_table(simple)
  tbl.classes:insert('edition-facts')
  return pandoc.Blocks({ tbl })
end

local function banner(id, e)
  local status = str(e.status)
  local label = str(e.label) or id
  local when = DERIVED.when(e)
  local venue = str(e.venue)
  local content = pandoc.Blocks({})
  local callout_type = 'note'
  local title

  if status == 'confirmed' then
    title = label .. ': confirmed'
    local p = pandoc.Inlines(pandoc.Str((when or TBC) .. '.'))
    if venue ~= nil then
      p:insert(pandoc.Space())
      p:insert(pandoc.Str(venue .. '.'))
    end
    content:insert(pandoc.Para(p))
  elseif status == 'delivered' then
    callout_type = 'tip'
    title = label .. ': archive'
    content:insert(pandoc.Para(pandoc.Inlines(pandoc.Str(
      'This edition took place on ' .. (when or TBC) .. '. The page keeps its information for reference.'
    ))))
  else
    title = label .. ': planned'
    content:insert(pandoc.Para(pandoc.Inlines(pandoc.Str(
      'The date, the venue, and the rules are not confirmed yet. Do not use the facts of another edition.'
    ))))
  end

  if quarto.doc.input_file:match('contents/editions/' .. id .. '%.qmd$') == nil then
    content:insert(pandoc.Para(pandoc.Inlines(pandoc.Link('Practical information for ' .. label, page_path(id)))))
  end

  return quarto.Callout({ type = callout_type, title = title, content = content })
end

local function list(meta)
  local all = editions(meta)
  local ids = {}
  for k, _ in pairs(all) do
    table.insert(ids, k)
  end
  -- Sort by date. An edition without a date goes last.
  table.sort(ids, function(a, b)
    local da = str(all[a].date) or '9999'
    local db = str(all[b].date) or '9999'
    if da == db then return a < b end
    return da < db
  end)
  local items = {}
  for _, id in ipairs(ids) do
    local e = all[id]
    local inl = pandoc.Inlines(pandoc.Link(str(e.label) or id, page_path(id)))
    inl:insert(pandoc.Str(' — ' .. (DERIVED.status(e) or TBC) .. '. ' .. (DERIVED.when(e) or ('Date: ' .. TBC)) .. '.'))
    table.insert(items, { pandoc.Plain(inl) })
  end
  return pandoc.Blocks({ pandoc.BulletList(items) })
end

local function evaluation(id, e)
  local url = str(e.evaluation_url)
  if url == nil then
    return text('The evaluation link follows on the course day.')
  end
  return pandoc.Inlines(pandoc.Link('Course evaluation for ' .. (str(e.label) or id), url))
end

return {
  ['edition'] = function(args, kwargs, meta)
    local id = args[1] and pandoc.utils.stringify(args[1]) or nil
    local field = args[2] and pandoc.utils.stringify(args[2]) or nil
    if id == nil or field == nil then
      quarto.log.error('edition shortcode: use {{< edition ID FIELD >}}.')
      return text(nil)
    end
    if id == 'all' and field == 'list' then
      return list(meta)
    end
    id = resolve_id(id, meta)
    local e = edition(id, meta)
    if e == nil then
      return text(nil)
    end
    if field == 'facts' then
      return facts_table(id, e)
    elseif field == 'banner' then
      return banner(id, e)
    elseif field == 'evaluation' then
      return evaluation(id, e)
    elseif field == 'page' then
      return pandoc.Inlines(pandoc.Link(str(e.label) or id, page_path(id)))
    elseif field == 'notes' then
      local items = {}
      for _, note in ipairs(e.notes or {}) do
        table.insert(items, { pandoc.Plain(pandoc.Inlines(pandoc.Str(str(note) or ''))) })
      end
      if #items == 0 then
        return pandoc.Blocks({ pandoc.Para(text('No further notes.')) })
      end
      return pandoc.Blocks({ pandoc.BulletList(items) })
    end
    local v = value(e, field)
    -- `link="Label"` turns a URL or an e-mail field into a link.
    local label = kwargs['link'] and pandoc.utils.stringify(kwargs['link']) or ''
    if label ~= '' and v ~= nil then
      local url = v
      if field == 'contact' then
        url = 'mailto:' .. v
      end
      return pandoc.Inlines(pandoc.Link(label, url))
    end
    return text(v)
  end
}
