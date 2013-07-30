#include <iostream>
#include "PPM_image.hpp"

int main(int argc, char *argv[])
{
	std::vector<std::string> arguments(argv, argv + argc);
	if (arguments.size() < 2)
	{
		std::cout << "Usage : " << argv[0] << " <input.ppm> [operation1] [operation2] ... <output.ppm>" << std::endl;
		std::cout << "\toperation# can be one of: 'edge' (sobel), 'blur' (gaussian blur), 'revert'" << std::endl;
		return 1;
	}

	// load image
	auto filename = argv[1];
	PPM_image input(filename);

	// get operations
	auto first_op = arguments.cbegin() + 2;
	auto last_op = arguments.cend() - 1;
	auto operations = std::vector<std::string>(first_op, last_op);

	std::cout << operations.size() << " operations" << std::endl;
	for (auto i = 0; i < operations.size(); i++)
	{
		std::cout << "#" << i << ": " << operations[i] << std::endl;
		if (operations[i] == "edge")
		{
			input.edge();
		}

		if (operations[i] == "blur")
		{
			input.gaussian_blur(1);
		}

		if (operations[i] == "revert")
		{
			input.revert();
		}

		
	}

	auto output_filename = arguments[arguments.size() - 1];
	input.save(output_filename);
	
	return 0;
}
