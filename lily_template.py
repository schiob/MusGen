TEMPLATE = r"""global = {
  \key $key \$grade
  \time 4/4
}

\parallelMusic #'(voiceA voiceB voiceC voiceD) {
  % Bar 1
$notes
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
}"""
