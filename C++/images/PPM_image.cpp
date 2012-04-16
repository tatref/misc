#include "PPM_image.hpp"

double gauss(double sigma, double x)
{
	return 1 / sqrt(2 * PI * sigma * sigma) * exp(-(x * x) / (2 * sigma * sigma));
}

PPM_image::PPM_image(const char* filename)
{
	std::ifstream file(filename);
	
	if(file.is_open())
	{
		std::string line;
		std::getline(file, line);
		
		// P6 = RAW
		// P3 = ASCII
		if(line != "P6")
		{
			std::cout << "Pas une image en PPM\n";
			exit(1);
		}
		
		std::getline(file, line);
		
		int max_value;
		file >> w >> h >> max_value;
		
		if(max_value != 255)
		{
			std::cout << "max_value != 255\n";
			exit(1);
		}
		
		file.get();
		
		pixels = new unsigned char[w * h * 3];
		file.read((char*)pixels, w * h * 3);
		
		file.close();
	}
}


PPM_image::PPM_image(const int width, const int height)
{
	w = width;
	h = height;
	
	pixels = new unsigned char[w * h * 3];
}

PPM_image::PPM_image(const PPM_image &image)
{
	w = image.w;
	h = image.h;
	
	pixels = new unsigned char[w * h * 3];
	
	for(int i = 0; i < w * h * 3; i++)
	{
		pixels[i] = image.pixels[i];
	}
}


PPM_image::~PPM_image()
{
	delete[] pixels;
}

unsigned char* PPM_image::get_pixel(const int x, const int y) const throw (int)
{
	if(x < 0 || x > w || y < 0 || y > h)
		throw 1;
		
	return &pixels[3 * (y * w + x)];
}

void PPM_image::save(const char* filename) const
{
	std::cout << "Saving file " << filename << "...\n";
	std::ofstream file(filename);
	
	if(file.is_open())
	{
		file << "P6\n# comment\n" << w << " " << h << "\n255\n";
		
		file.write((char*)pixels, w * h * 3);
	}
	
	file.close();
	std::cout << "Ok\n";
}

void PPM_image::gaussian_blur(const int str)
{
	std::cout << "Gaussian blur...\n";
	
	// Create kernel
	double** mat = new double*[2 * str];
	
	for(int i = 0; i < 2 * str; i++)
	{
		mat[i] = new double[2 * str];
		
		for(int j = 0; j < 2 * str; j++)
		{
			mat[i][j] = gauss(str, sqrt((i - str) * (i - str) + (j - str) * (j - str)));
		}
	}
	
	for (int i = 0; i < w; i++)
	{
		std::cout << "\r" << (int)(100 * (float)(i + 1) / (float)w) << "%";
		
		for (int j = 0; j < h; j++)
		{
			double r = 0, g = 0, b = 0;
			double coeff = 0;
			
			for (int k = -str; k < str; k++)
			{
				for (int l = -str; l < str; l++)
				{
					try
					{
						unsigned char *p = get_pixel(i + k, j + l);
						
						double norm = mat[k + str][l + str];
						
						r += *p * norm;
						g += *(p + 1) * norm;
						b += *(p + 2) * norm;
						
						coeff += norm;
					}
					catch(int n)
					{
					
					}
				}
			}
			
			unsigned char *p = get_pixel(i, j);
			
			if(coeff > 0)
			{
				*p = (int)(r / coeff);
				*(p + 1) = (int)(g / coeff);
				*(p + 2) = (int)(b / coeff);
			}
		}
	}
	
	delete[] mat;
	
	std::cout << "\n";
}

void PPM_image::test()
{
	std::cout << "Test...\n";
	
	unsigned char min = 255, max = 0;
	
	// Find max & min
	for (int i = 0; i < w * h * 3; i++)
	{	
		if(pixels[i] > max)
		{
			max = pixels[i];
		}
		
		if(pixels[i] < min)
		{
			min = pixels[i];
		}
	}
	
	// y = a.x + b
	float a = ((float)255) / ((float)(max - min));
	float b = (((float)-255) * (float)min) / ((float)(max - min));
	
	for (int i = 0; i < w * h * 3; i++)
	{
		pixels[i] = a * pixels[i] + b;
	}
}


void PPM_image::edge()
{
	std::cout << "Edge detection...\n";
	PPM_image img(*this);
	
	for (int i = 1; i < w - 1; i++)
	{
		std::cout << "\r" << (int)(100 * (float)(i + 2) / (float)w) << "%";
		std::cout.flush();
		for (int j = 1; j < h - 1; j++)
		{
			int val = 0;
			
			for(int k = 0; k < 3; k++)
			{
				int Gx = *(img.get_pixel(i - 1, j - 1) + k) + 2 * (*(img.get_pixel(i, j - 1) + k)) + *(img.get_pixel(i + 1, j - 1) + k)
					- *(img.get_pixel(i - 1, j + 1) + k) - 2 * (*(img.get_pixel(i, j + 1) + k)) - *(img.get_pixel(i + 1, j + 1) + k);
				int Gy = *(img.get_pixel(i - 1, j - 1) + k) + 2 * (*(img.get_pixel(i - 1, j) + k)) + *(img.get_pixel(i - 1, j + 1) + k)
					- *(img.get_pixel(i + 1, j - 1) + k) - 2 * (*(img.get_pixel(i + 1, j) + k)) - *(img.get_pixel(i + 1, j + 1) + k);
				int G = sqrt(Gx * Gx + Gy * Gy);
				
				val += G;
			}
			
			val /= 3;
			
			for(int k = 0; k < 3; k++)
			{
				if(val > 255)
				{
					*(get_pixel(i, j) + k) = 255;
				}
				else
				{
					*(get_pixel(i, j) + k) = val;
				}
			}
		}
	}
	
	std::cout << "\n";
}

void PPM_image::revert()
{
	std::cout << "Reverting...\n";
	
	for(int i = 0; i < w * h * 3; i++)
	{
		pixels[i] = 255 - pixels[i];
	}
	
	std::cout << "Ok\n";
}

void PPM_image::add(PPM_image &image)
{
	for(int i = 0; i < w * h * 3; i++)
	{
		pixels[i] = (pixels[i] + image.pixels[i]) / 2;
	}
}
