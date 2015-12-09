global = {
  \key g \major
  \time 4/4
}

\parallelMusic #'(voiceA voiceB voiceC voiceD) {
  % Bar 1
b' a' c'' d'' c'' d'' c'' c'' d'' e'' b' a' a' b' c'' g' c'' b' g' b' d'' fis' g'|
d' d' e' fis' e' g' e' g' fis' a' g' fis' d' d' e' d' e' d' e' e' fis' d' d'|
g fis g g a b c' c' d' e' e' a fis g e g g g g g a d g|
g, d c b, a, g, g e d c e d d g, a, b, c b, c e d d, g,|
  % Bar 2 ...
}

\score {
  \new PianoStaff <<
     \new Staff {
       \global
       <<
         \voiceA
         \\
         \voiceB
       >>
     }
     \new Staff {
       \global \clef bass
       <<
         \voiceC
         \\
         \voiceD
       >>
     }
  >>
  \layout{}
  \midi{}
}