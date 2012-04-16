# makefile

CC=cc
CFLAGS=-Wall -lm -lpthread -O3 -march=native -g -std=c99

all: raytracer

raytracer: main.o vector3.o
	$(CC) $(CFLAGS) main.o vector3.o -o raytracer

clean:
	rm -rf *.o raytracer
