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
	# create flash disk image
	dd if=/dev/zero of=flash.bin bs=4096 count=4096

	# assemble
	$(AS) $(target).s -o $(target).o

	# link
	$(LD) $(LD_OPTIONS) $(target).o -o $(target).elf

	# convert elf to bin format
	$(OBJCOPY) $(OBJCOPY_OPTIONS) $(target).elf $(target).bin

	# add binary to disk
	dd if=$(target).bin of=flash.bin conv=notrunc

run:
	# -S: pause CPU at startup (c to continue)
	# -s: enable gdbserver on port 1234
	qemu-system-arm -s -S -M connex -pflash flash.bin -nographic -serial /dev/null

clean:
	rm -f $(target).bin $(target).elf $(target).o flash.bin
