# makefile

CC=gcc
CFLAGS=-Wall -O3 -march=native -g -std=c99 -lm -lpthread

all: raytracer

raytracer: main.o vector3.o
	$(CC) main.o vector3.o -o raytracer $(CFLAGS)

clean:
	rm -rf *.o raytracer
