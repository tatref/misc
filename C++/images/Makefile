# makefile

CC=clang++

CFLAGS=-Wall -O3 -march=native -g -std=c++11
LDFLAGS=-lm

OBJS=main.o PPM_image.o



all: image


image: $(OBJS)
	$(CC) $(LDLAGS) $(OBJS) -o image

main.o:
	$(CC) -c $(CFLAGS) main.cpp -o main.o

PPM_image.o:
	$(CC) -c $(CFLAGS) PPM_image.cpp -o PPM_image.o


clean:
	rm -rf *.o image
