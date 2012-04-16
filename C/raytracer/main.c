#include <stdio.h>
#include <stdlib.h>
#include "vector3.h"
#include <math.h>
#include <time.h>
#include <pthread.h>
#include <signal.h>
#include <unistd.h>

/* types of objects */
#define SPHERE 1
#define TRIANGLE 2

#define MAX_DEPTH 10

#define PI 3.14159265

int running = 1;

typedef struct
{
	unsigned char b;
	unsigned char g;
	unsigned char r;
} Pixel;

typedef struct
{
	float b;
	float g;
	float r;
} Color;

typedef struct
{
	vector3* center;
	float r;
} Sphere;

typedef struct
{
	vector3* u, *v, *w;
} Triangle;

typedef struct
{
	int type;
	void* object;
	Color* reflectance;
	Color* emittance;
	float coeff_reflec, coeff_refrac;
} Object;


typedef struct
{
	vector3* org;
	vector3* dir;
} Ray;

typedef struct
{
	Ray* ray;
	vector3* up;
	float width, height;
	int resX, resY;
} Camera;

typedef struct
{
	Camera* camera;
	Object** objects;
	int objects_count;
	Color*** data;
	Color* background;
} Scene;


void printVector3(const vector3* v);
void printPixel(const Pixel* p);

int Color_equals(const Color* c1, const Color* c2)
{
	if(c1->r != c2->r)
	{
		return 0;
	}
	if(c1->g != c2->g)
	{
		return 0;
	}
	if(c1->b != c2->b)
	{
		return 0;
	}
	
	return 1;
}

Color* Color_copy(const Color* c)
{
	Color* res = malloc(sizeof(Color));
	
	res->r = c->r;
	res->g = c->g;
	res->b = c->b;
	
	return res;
}

void Color_add(Color* dst, const Color* c1, const Color* c2)
{
	dst->r = c1->r + c2->r;
	dst->g = c1->g + c2->g;
	dst->b = c1->b + c2->b;
}

Color* Color_f_multiply(const Color* c, float val)
{
	Color* res = malloc(sizeof(Color));
	
	res->r = c->r * val;
	res->g = c->g * val;
	res->b = c->b * val;
	
	return res;
}

Color* Color_c_multiply(const Color* c1, const Color* c2)
{
	Color* res = malloc(sizeof(Color));
	
	res->r = c1->r * c2->r;
	res->g = c1->g * c2->g;
	res->b = c1->b * c2->b;
	
	return res;
}

Color* Color_divide(const Color* c, float val)
{
	Color* res = malloc(sizeof(Color));
	
	res->r = c->r / val;
	res->g = c->g / val;
	res->b = c->b / val;
	
	return res;
}


Camera* defaultCamera()
{
	Camera* camera = malloc(sizeof(Camera));
	Ray* ray = malloc(sizeof(Ray));
	
	ray->org = malloc(sizeof(vector3));
	ray->org->x = 0;
	ray->org->y = 0;
	ray->org->z = 0;
	
	ray->dir = malloc(sizeof(vector3));
	ray->dir->x = 1;
	ray->dir->y = 0;
	ray->dir->z = 0;
	
	camera->ray = ray;
	
	vector3* up = malloc(sizeof(vector3));
	up->x = 0;
	up->y = 0;
	up->z = 1;
	
	camera->up = up;
	
	camera->resX = 100;
	camera->resY = 100;
	
	camera->width = 100;
	camera->height = 100;
	
	return camera;
}

void* create_sphere(float cx, float cy, float cz, float r, float rr, float rg, float rb, float er, float eg, float eb)
{
	Object* res = malloc(sizeof(Object));
	res->type = SPHERE;
	
	res->reflectance = malloc(sizeof(Color));
	res->reflectance->r = rr;
	res->reflectance->g = rg;
	res->reflectance->b = rb;
	
	res->emittance = malloc(sizeof(Color));
	res->emittance->r = er;
	res->emittance->g = eg;
	res->emittance->b = eb;
	
	Sphere* s = malloc(sizeof(Sphere));
	res->object = s;
	s->center = malloc(sizeof(vector3));
	s->center->x = cx;
	s->center->y = cy;
	s->center->z = cz;
	s->r = r;
	
	return res;
}

void deleteSphere(Object* object)
{
	free(((Sphere*)object->object)->center);
	free((Sphere*)object->object);
	free(object->emittance);
	free(object->reflectance);
	free(object);
}

Scene* defaultScene()
{
	Scene* scene = malloc(sizeof(Scene));
	
	scene->camera = defaultCamera();
	
	scene->objects_count = 3;
	scene->objects = malloc(scene->objects_count * sizeof(Object*));
	
	/* cx, cy, cz, r, rr, rg, rb, er, eg, eb */
	scene->objects[0] = create_sphere(20, 0, -10, 10, 0, 0, 0, 0, 0, 1);
	scene->objects[1] = create_sphere(20, 0, 10, 5, 100, 100, 100, 0, 0, 0);
	scene->objects[2] = create_sphere(20, 0, 20, 5, 0, 0, 0, 1, 0, 0);
	//scene->objects[2] = create_sphere(20, 20, 20, 5, 10, 10, 10, 0, 0, 0);
	
	scene->background = malloc(sizeof(Color));
	scene->background->r = 0;
	scene->background->g = 0;
	scene->background->b = 0;
	
	scene->data = malloc(scene->camera->resY * sizeof(Color**));
	
	int y;
	for(y = 0; y < scene->camera->resY; y++)
	{
		scene->data[y] = malloc(scene->camera->resX * sizeof(Color*));
		
		int x;
		for(x = 0; x < scene->camera->resX; x++)
		{
			// free & malloc in render
			scene->data[y][x] = malloc(sizeof(Color));
			
			scene->data[y][x]->r = 0;
			scene->data[y][x]->g = 0;
			scene->data[y][x]->b = 0;
		}
	}
	
	return scene;
}

void deleteScene(Scene* scene)
{
	int y;
	for(y = 0; y < scene->camera->resY; y++)
	{
		int x;
		for(x = 0; x < scene->camera->resX; x++)
		{
			free(scene->data[y][x]);
		}
		
		free(scene->data[y]);
	}
	free(scene->data);
	
	free(scene->background);
	
	int i;
	for(i = 0; i < scene->objects_count; i++)
	{
		if(scene->objects[i]->type == SPHERE)
		{
			deleteSphere(scene->objects[i]);
		}
	}
	free(scene->objects);
	
	free(scene->camera->ray->org);
	free(scene->camera->ray->dir);
	free(scene->camera->ray);
	free(scene->camera->up);
	free(scene->camera);

	free(scene);
}

float intersectRayTri(const Ray* ray, const Triangle* tri)
{
	return -1;
}

float intersectRaySphere(const Ray* ray, const Sphere* sphere)
{
	vector3* dst = malloc(sizeof(vector3));
	dst->x = 0;
	dst->y = 0;
	dst->z = 0;
	
	vector3_subtract(dst, ray->org, sphere->center);
	
	float B = vector3_dot(dst, ray->dir);
	float C = vector3_dot(dst, dst) - sphere->r * sphere->r;
	float D = B * B - C;
	
	free(dst);
	
	if(D > 0)
	{
		// Intersection
		return -B - sqrt(D);
	}
	else
	{
		// No intersection
		return -1;
	}
}

void printCamera(const Camera* camera)
{
	printf("org(%f, %f, %f), dir(%f, %f, %f), up(%f, %f, %f)\n", camera->ray->org->x, camera->ray->org->y, camera->ray->org->z, camera->ray->dir->x, camera->ray->dir->y, camera->ray->dir->z, camera->up->x, camera->up->y, camera->up->z);
}

void printSphere(const Sphere* sphere)
{
	printf("center(%f, %f, %f), r=%f\n", sphere->center->x, sphere->center->y, sphere->center->z, sphere->r);
}

void printPixel(const Pixel* p)
{
	printf("%i, %i, %i\n", p->r, p->g, p->b);
}

void Color_print(const Color* c)
{
	printf("%f, %f, %f\n", c->r, c->g, c->b);
}

vector3* random_vector_from_normal(vector3* normal)
{
	vector3* v = malloc(sizeof(vector3));
	do
	{
		v->x = (double)rand()/RAND_MAX*2-1;
		v->y = (double)rand()/RAND_MAX*2-1;
		v->z = (double)rand()/RAND_MAX*2-1;
	} while(vector3_dot(normal, v) < 0);
	
	vector3_normalize(v);
	
	return v;
}

Object* find_nearest_object(const Ray* ray, const Scene* scene, float* dist, const Object* dont_hit)
{
	float minDist = 99999;
	Object* hit = NULL;
	
	for(int nb = 0; nb < scene->objects_count; nb++)
	{
		if(scene->objects[nb] != dont_hit)
		{
			if(scene->objects[nb]->type == SPHERE)
			{
				Sphere* s = scene->objects[nb]->object;
				*dist = intersectRaySphere(ray, s);
			
				if(*dist > 0 && *dist < minDist)
				{
					minDist = *dist;
					hit = scene->objects[nb];
				}
			}
			if(scene->objects[nb]->type == TRIANGLE)
			{
				Triangle* t = scene->objects[nb]->object;
				*dist = intersectRayTri(ray, t);
			
				if(*dist > 0 && *dist < minDist)
				{
					minDist = *dist;
					hit = scene->objects[nb];
				}
			}
		}
	}	
	
	return hit;
}

vector3* Sphere_normal_at(const vector3* pos, const Sphere* sphere)
{
	vector3* res = malloc(sizeof(vector3));
	vector3_subtract(res, pos, sphere->center);
	
	vector3_normalize(res);
	
	return res;
}

Color* trace_path(const Ray* ray, const Scene* scene, int depth, const Object* last_hit)
{
	if(depth == MAX_DEPTH)
	{
		return Color_copy(scene->background);
	}
	
	float dist = 0;
	Object* hit = find_nearest_object(ray, scene, &dist, last_hit);
	
	if(hit == NULL)
	{
		return Color_copy(scene->background);
	}
	
	/*
	if(last_hit == scene->objects[1])
	{
		printf("plop\n");
		if(hit == scene->objects[0])
			printf("0\n");
		if(hit == scene->objects[2])
			printf("2\n");
		return Color_copy(hit->emittance);
	}
	*/
	
	Color* emittance = hit->emittance;
	Color* reflectance = hit->reflectance;
	
	Ray* newRay = malloc(sizeof(Ray));
	newRay->org = malloc(sizeof(vector3));
	vector3_multiply(newRay->org, ray->dir, dist);
	vector3_add(newRay->org, newRay->org, ray->org);
	
	vector3* normal;
	if(hit->type == SPHERE)
	{
		normal = Sphere_normal_at(newRay->org, (Sphere*)hit->object);
	}
	else
	{
		normal = NULL;
	}
	
	newRay->dir = random_vector_from_normal(normal);
	float cost = vector3_dot(newRay->dir, normal);
	
	Color* BRDF = Color_divide(reflectance, PI);
	float scale = 1.0 / PI;
	Color* reflected = trace_path(newRay, scene, depth + 1, hit);
	
	Color* tmp2 = Color_c_multiply(reflected, BRDF);
	Color* tmp = Color_f_multiply(tmp2, scale * cost);
	Color* result = malloc(sizeof(Color));
	Color_add(result, tmp, emittance);
	
	/* free */
	free(normal);
	free(BRDF);
	free(reflected);
	free(tmp);
	free(tmp2);
	free(newRay->org);
	free(newRay->dir);
	free(newRay);
	
	return result;
}

/*
vector3* random_dir_camera(Camera* camera)
{
	
}
*/

void render2(Scene* scene)
{
	/* outside of loop for opt */
	Ray* ray = malloc(sizeof(Ray));
	ray->org = malloc(sizeof(vector3));
	ray->dir = scene->camera->ray->dir;
	vector3* right = malloc(sizeof(vector3));
	vector3_cross(right, scene->camera->ray->dir, scene->camera->up);
	
	Color* tmp;
	float i, j;
	int k;
	
	k=0;

	while(running)
	{
		i = ((float)rand() / (float)RAND_MAX) * (float)scene->camera->resX - 1;
		j = ((float)rand() / (float)RAND_MAX) * (float)scene->camera->resY - 1;
		
		vector3* offset_h = malloc(sizeof(vector3));
		vector3_multiply(offset_h, right, -scene->camera->width / 2);
		vector3* tmp_h = malloc(sizeof(vector3));
		vector3_multiply(tmp_h, right, i * scene->camera->width / scene->camera->resX);
		vector3_add(offset_h, tmp_h, offset_h);
	
		/* vertical */
		vector3* offset_v = malloc(sizeof(vector3));
		vector3_multiply(offset_v, scene->camera->up, -scene->camera->height / 2);
		vector3* tmp_v = malloc(sizeof(vector3));
		vector3_multiply(tmp_v, scene->camera->up, j * scene->camera->height / scene->camera->resY);
		vector3_add(offset_v, tmp_v, offset_v);
	
		/* add vertical and horizontal offsets to org camera */
		vector3_add(ray->org, scene->camera->ray->org, offset_h);
		vector3_add(ray->org, ray->org, offset_v);
	
		free(offset_h);
		free(tmp_h);
		free(offset_v);
		free(tmp_v);
		
		tmp = trace_path(ray, scene, 0, NULL);
		
		Color* c = scene->data[(int)j][(int)i];
		Color_add(c, c, tmp);
		
		free(tmp);
	}
	
	free(ray->org);
	free(ray);
	free(right);
}

void writeBMP(Color*** data, int width, int height, int bpp, char* filename)
{
	FILE* f = fopen(filename, "wb");
	printf("%s\n", filename);
	
	int* intpt = malloc(sizeof(int));
	short* shortpt = malloc(sizeof(short));
	
	/*****
	header
	******/
	/* magic number */
	char* magic_number = "BM";
	fwrite(magic_number, 1, 2, f);
	
	/* size of the file */
	*intpt = 54 + width * height * 3;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* application specific */
	*intpt = 0;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* data offset */
	*intpt = 54;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* size of header (from here) */
	*intpt = 40;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* width */
	*intpt = width;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* height */
	*intpt = height;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* number of color planes */
	*shortpt = 1;
	fwrite(shortpt, 1, sizeof(short), f);
	
	/* bits per pixel */
	*shortpt = bpp;
	fwrite(shortpt, 1, sizeof(short), f);
	
	/* compression */
	*intpt = 0;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* size of raw data */
	*intpt = width * height * 3;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* horizontal resolution (p/m) */
	*intpt = 1;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* vertical resolution */
	*intpt = 1;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* number of colors in the palette */
	*intpt = 0;
	fwrite(intpt, 1, sizeof(int), f);
	
	/* important colors */
	*intpt = 0;
	fwrite(intpt, 1, sizeof(int), f);
	
	/*********
	end header
	**********/
	
	/***
	data
	****/
	Pixel* pixel = malloc(sizeof(Pixel));
	
	for(int x = 0; x < width; x++)
	{
		for(int y = 0; y < height; y++)
		{
			pixel->r = (char)data[y][x]->r;
			pixel->g = (char)data[y][x]->g;
			pixel->b = (char)data[y][x]->b;
			
			fwrite(pixel, 1, sizeof(Pixel), f);
		}
	}
	free(pixel);
	
	/*******
	end data
	********/
	
	free(intpt);
	free(shortpt);
	
	fclose(f);
}

void tonemapping(Scene* scene)
{
	float max = 0;
	for(int i = 0; i < scene->camera->resX; i++)
	{
		for(int j = 0; j < scene->camera->resY; j++)
		{
			if(scene->data[j][i]->r > max)
			{
				max = scene->data[j][i]->r;
			}
			if(scene->data[j][i]->g > max)
			{
				max = scene->data[j][i]->g;
			}
			if(scene->data[j][i]->b > max)
			{
				max = scene->data[j][i]->b;
			}
			
		}
	}
	
	for(int i = 0; i < scene->camera->resX; i++)
	{
		for(int j = 0; j < scene->camera->resY; j++)
		{
			scene->data[j][i]->r = (scene->data[j][i]->r * 255) / max;
			scene->data[j][i]->g = (scene->data[j][i]->g * 255) / max;
			scene->data[j][i]->b = (scene->data[j][i]->b * 255) / max;
		}
	}
}

Scene* scene;

void interrupt(int sig)
{
	running = 0;

	tonemapping(scene);
	printf("tonemapping OK\n");
	
	writeBMP(scene->data, scene->camera->resX, scene->camera->resY, 24, "test.bmp");
	printf("writeBMP OK\n");
	
	// Wait for other threads to end
	sleep(1);
	
	deleteScene(scene);
	printf("Interrupted\n");
	
	exit(sig);
}

void* main_render(void* p)
{
	srand (time(NULL));

	scene = defaultScene();
	printf("defaultScene OK\n");
	
	printf("rendering...\n");
	render2(scene);
	
	return 0;
}

void* main_save(void* p)
{
	while(running)
	{
		sleep(10);
		
		tonemapping(scene);
		writeBMP(scene->data, scene->camera->resX, scene->camera->resY, 24, "test.bmp");
		printf("writeBMP OK\n");
	}
	
	return 0;
}

int main(int argc, char** argv)
{
	// CTRL-C
	signal(SIGINT, interrupt);
	
	pthread_t render_thread, save_thread;
	
	pthread_create( &render_thread, NULL, main_render, (void*) NULL);
	pthread_create( &save_thread, NULL, main_save, (void*) NULL);
	
	// Wait for threads to finish
	pthread_join(render_thread, NULL);
	pthread_join(save_thread, NULL);
	
	return 0;
}
