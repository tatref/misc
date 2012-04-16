#include <iostream>
#include "PPM_image.hpp"

int main(int argc, char *argv[])
{
	if(argc < 2)
	{
		std::cout << "Usage : " << argv[0] << "input.ppm" << std::endl;
		return 1;
	}
	
	PPM_image input(argv[1]);
	
	input.edge();

	input.save("output.ppm");
	
	return 0;
}
