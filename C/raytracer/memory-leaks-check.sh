#!/bin/sh

valgrind --tool=memcheck --leak-check=yes ./$1
