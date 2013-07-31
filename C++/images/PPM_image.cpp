#include "PPM_image.hpp"

double gauss(double sigma, double x)
{
	return 1 / sqrt(2 * PI * sigma * sigma) * exp(-(x * x) / (2 * sigma * sigma));
}

PPM_image::PPM_image(std::string filename)
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
			std::cout << "Not a PPM image" << std::endl;
			exit(1);
		}
		
		std::getline(file, line);
		
		int max_value;
		file >> w >> h >> max_value;
		
		if(max_value != 255)
		{
			std::cout << "max_value != 255" << std::endl;
			exit(1);
		}
		
		file.get();
		
		pixels = new unsigned char[w * h * 3];
		file.read((char*)pixels, w * h * 3);
		
		file.close();
	}
}


PPM_image::PPM_image(const decltype(w) width, const decltype(h) height)
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
	
	for (auto i = 0; i < w * h * 3; i++)
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
	{
		throw 1;
	}
		
	return &pixels[3 * (y * w + x)];
}

void PPM_image::save(std::string filename) const
{
	std::cout << "Saving file " << filename << "...";
	std::ofstream file(filename);
	
	if(file.is_open())
	{
		file << "P6\n# comment\n" << w << " " << h << "\n255\n";
		
		file.write((char*)pixels, w * h * 3);
	}
	
	file.close();
	std::cout << "Ok" << std::endl;
}

void thread_blur(PPM_image* src, PPM_image* dst, int start_line, int end_line, int str)
{
	
	// Create kernel
	double mat[2 * str][2 * str];
	
	for (auto i = 0; i < 2 * str; i++)
	{
		for (auto j = 0; j < 2 * str; j++)
		{
			mat[i][j] = gauss(str, sqrt((i - str) * (i - str) + (j - str) * (j - str)));
		}
	}

	for (auto i = 0; i < src->w; i++)
	{
		//std::cout << "\r" << (int)(100 * (float)(i + 1) / (float)w) << "%";
		
		for (auto j = start_line; j < end_line; j++)
		{
			auto r = 0.0, g = 0.0, b = 0.0;
			auto coeff = 0.0;
			
			for (auto k = -str; k < str; k++)
			{
				for (auto l = -str; l < str; l++)
				{
					try
					{
						auto* p = src->get_pixel(i + k, j + l);
						
						auto norm = mat[k + str][l + str];
						
						r += *p * norm;
						g += *(p + 1) * norm;
						b += *(p + 2) * norm;
						
						coeff += norm;
					}
					catch(const int& n)
					{
					
					}
				}
			}
			
			auto* p = dst->get_pixel(i, j);
			
			if(coeff > 0)
			{
				*p = (int)(r / coeff);
				*(p + 1) = (int)(g / coeff);
				*(p + 2) = (int)(b / coeff);
			}
		}
	}
}

void PPM_image::gaussian_blur(const int str)
{
	std::cout << "Gaussian blur..." << std::endl;
	PPM_image img(*this);

	auto n_threads = std::thread::hardware_concurrency();
	std::vector<std::thread> threads;
	std::cout << "Launching " << n_threads << " threads" << std::endl;
	for (auto i = 0l; i < n_threads; i++)
	{
		std::cout << "Thread #" << i << " start=" << i * h / n_threads << ", end=" << (i + 1) * h / n_threads << std::endl;
		threads.push_back(std::thread(thread_blur, this, &img, i * h / n_threads, (i + 1) * h / n_threads, str));
	}

	for (auto &t : threads)
	{
		t.join();
	}

	std::copy(img.pixels, img.pixels + img.w * img.h * 3, this->pixels);

}

void thread_edge(PPM_image* src, PPM_image* dst, int start_line, int end_line)
{
	for (auto i = 1; i < src->w - 1; i++)
	{
		for (auto j = start_line; j < end_line; j++)
		{
			auto val = 0;
			for (auto k = 0; k < 3; k++)
			{
				auto Gx = *(src->get_pixel(i - 1, j - 1) + k) + 2 * (*(src->get_pixel(i, j - 1) + k)) + *(src->get_pixel(i + 1, j - 1) + k)
					- *(src->get_pixel(i - 1, j + 1) + k) - 2 * (*(src->get_pixel(i, j + 1) + k)) - *(src->get_pixel(i + 1, j + 1) + k);
				auto Gy = *(src->get_pixel(i - 1, j - 1) + k) + 2 * (*(src->get_pixel(i - 1, j) + k)) + *(src->get_pixel(i - 1, j + 1) + k)
					- *(src->get_pixel(i + 1, j - 1) + k) - 2 * (*(src->get_pixel(i + 1, j) + k)) - *(src->get_pixel(i + 1, j + 1) + k);
				auto G = sqrt(Gx * Gx + Gy * Gy);
				
				val += G;
			}
			
			val /= 3;
			
			for (auto k = 0; k < 3; k++)
			{
				if(val > 255)
				{
					*(dst->get_pixel(i, j) + k) = 255;
				}
				else
				{
					*(dst->get_pixel(i, j) + k) = val;
				}
			}
		}
	}
}

void PPM_image::edge()
{
	std::cout << "Edge detection..." << std::endl;
	PPM_image img(*this);
	
	auto n_threads = std::thread::hardware_concurrency();
	std::vector<std::thread> threads;
	std::cout << "Launching " << n_threads << " threads" << std::endl;
	for (auto i = 0l; i < n_threads; i++)
	{
		std::cout << "Thread #" << i << " start=" << i * (h - 2) / n_threads + 1 << ", end=" << (i + 1) * (h - 2) / n_threads + 1 << std::endl;
		threads.push_back(std::thread(thread_edge, this, &img, i * (h - 2) / n_threads + 1, (i + 1) * (h - 2) / n_threads + 1));
	}

	for (auto &t : threads)
	{
		t.join();
	}

	std::copy(img.pixels, img.pixels + img.w * img.h * 3, this->pixels);
}

void thread_revert(PPM_image* img, int start_range, int end_range)
{
	for (auto i = start_range; i < end_range; i++)
	{
		img->pixels[i] = 255 - img->pixels[i];
	}
}

void PPM_image::revert()
{
	std::cout << "Reverting..." << std::endl;

	auto n_threads = std::thread::hardware_concurrency();
	std::vector<std::thread> threads;
	std::cout << "Launching " << n_threads << " threads" << std::endl;
	for (auto i = 0l; i < n_threads; i++)
	{
		threads.push_back(std::thread(thread_revert, this, i * w * h * 3 / n_threads, (i + 1) * w * h * 3 / n_threads));
	}

	for (auto &t : threads)
	{
		t.join();
	}
	
	std::cout << "Ok" << std::endl;
}

void PPM_image::add(PPM_image &image)
{
	for (auto i = 0; i < w * h * 3; i++)
	{
		pixels[i] = (pixels[i] + image.pixels[i]) / 2;
	}
}
