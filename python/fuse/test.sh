#!/bin/bash

> my_fs.log
tail -f my_fs.log &
pid_of_tail=$!

./my_fs.py fs
sleep 0.5


ls -al fs/T.I
time dd if=fs/T.I/What\ You\ Know.mp3 bs=64 count=1
time dd if=fs/T.I/What\ You\ Know.mp3 bs=64 count=1


sleep 1
kill $pid_of_tail
fusermount -u fs
