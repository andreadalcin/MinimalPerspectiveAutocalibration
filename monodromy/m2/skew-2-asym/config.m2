needsPackage "MonodromySolver"

E = new HashTable from {
    symbol fxi => symbol fxi,
    symbol fyi => symbol fyi,
    symbol cx => symbol cx,
    symbol cy => symbol cy,
    symbol s  => symbol zer0
};

C = {{0,1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18},{0,1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18},{0,1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18}}

-- Monodromy
MonodromyStepMin = 1e-8
MonodromyBatchSize = 1000