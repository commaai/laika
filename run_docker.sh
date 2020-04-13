# Build image
docker build -t rwschubert/kalman-laika .

# Clean output
rm -rf output/*

# Run image
docker run \
    --rm \
    -v `pwd`/data:/workdir/data \
    -v `pwd`/cache:/workdir/cache \
    -v `pwd`/output:/workdir/output \
    rwschubert/kalman-laika \
    run_filter.py