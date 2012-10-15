
all: test.o
	ld -o test test.o

clean:
	rm -f test test.o

test.o:
	nasm -f elf -o test.o test.as
	
