#!/bin/bash

./my_fs.py fs
sleep 0.5

ls -al fs

find fs -type f -exec ls -al {} \;


sleep 0.5
fusermount -u fs
