#!/bin/bash

dd if=/dev/urandom of=25MB.test bs=25M iflag=fullblock count=1
dd if=/dev/urandom of=50MB.test bs=50M iflag=fullblock count=1
dd if=/dev/urandom of=100MB.test bs=100M iflag=fullblock count=1