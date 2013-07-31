# makefile

CC=clang++

CFLAGS=-Wall -O3 -march=native -g -std=c++11
LDFLAGS=-lm -lpthread

OBJS=main.o PPM_image.o



all: image


image: $(OBJS)
	$(CC) $(LDFLAGS) $(OBJS) -o image

main.o: main.cpp
	$(CC) -c $(CFLAGS) main.cpp -o main.o

PPM_image.o: PPM_image.cpp
	$(CC) -c $(CFLAGS) PPM_image.cpp -o PPM_image.o


clean:
	rm -rf *.o image
