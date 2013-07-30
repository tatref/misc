#ifndef PPM_IMAGE_HPP
#define PPM_IMAGE_HPP

#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <sstream>
#include <vector>
#include <thread>

#define PI 3.141592653589


double gauss(double sigma, double x);

class PPM_image
{
public:
	// Attributes
	int w, h;
	unsigned char* pixels;
	//std::vector<unsigned char> pixels;
	
	
	// Constructors
	PPM_image(std::string filename);
	PPM_image(const int width, const int height);
	PPM_image(const PPM_image &image);
	~PPM_image();
	
	// Utilities
	//unsigned char* get_pixel(const int x, const int y) const throw (int);
	decltype(pixels) get_pixel(const decltype(w) x, const decltype(h) y) const throw (int);
	void save(std::string name) const;
	
	// Manipulation
	void gaussian_blur(const int str);
	void edge();
	void test();
	void add(PPM_image &image);
	void revert();
};

#endif
