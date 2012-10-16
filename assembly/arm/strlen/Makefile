#
# Makefile to build ARM assembly
#

# utils
AS = ../arm-2012.03/bin/arm-none-linux-gnueabi-as
LD = ../arm-2012.03/bin/arm-none-linux-gnueabi-ld
OBJCOPY = ../arm-2012.03/bin/arm-none-linux-gnueabi-objcopy

# options
LD_OPTIONS = -Ttext=0x0
OBJCOPY_OPTIONS = -O binary
target = main


all:
	dd if=/dev/zero of=flash.bin bs=4096 count=4096
	
	$(AS) $(target).s -o $(target).o
	$(LD) $(LD_OPTIONS) $(target).o -o $(target).elf
	$(OBJCOPY) $(OBJCOPY_OPTIONS) $(target).elf $(target).bin
	
	dd if=./$(target).bin of=flash.bin conv=notrunc

run: 
	qemu-system-arm -M connex -pflash flash.bin -nographic -serial /dev/null

clean:
	rm -f $(target).bin $(target).elf $(target).o flash.bin
