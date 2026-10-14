// Shared print settings for the handouts (Typst).
// Ragged-right text without hyphenation is easier to read.
#set par(justify: false)
#set text(hyphenate: false)
// A light grid gives every cell a visible box to write in.
#set table(stroke: 0.6pt + rgb("#8f8d88"), inset: 6pt)
#show heading: set block(above: 1.1em, below: 0.5em, sticky: true)
