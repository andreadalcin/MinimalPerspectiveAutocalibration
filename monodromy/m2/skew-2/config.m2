needsPackage "MonodromySolver"

E = new HashTable from {{
    symbol fxi => symbol {fxi},
    symbol fyi => symbol {fyi},
    symbol cx => symbol {cx},
    symbol cy => symbol {cy},
    symbol s  => symbol {s}
}};

C = {{{configs}}}

-- Monodromy
MonodromyStepMin = 1e-8
MonodromyBatchSize = 1000