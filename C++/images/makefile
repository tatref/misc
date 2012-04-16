# makefile

CC=g++
CFLAGS=-Wall -lm -O3 -march=native -g

all: image

image: main.o PPM_image.o
	$(CC) $(CFLAGS) main.o PPM_image.o -o image

clean:
	rm -rf *.o image
