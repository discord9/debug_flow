#!/usr/bin/env bash

set -x

export IMAGE_TAG="v0.11.09"

docker build -f ./Dockerfile -t localhost:5001/nightly-greptimedb:${IMAGE_TAG} .

docker push localhost:5001/nightly-greptimedb:${IMAGE_TAG}