/* Various signal processing operations on memory buffers.  
 */

#include <stdio.h>
#include <math.h>

#include <glib.h>

#define RMS(TYPE) { \
	TYPE *p; \
	int n_samples; \
	\
	n_samples = (len / channels) / sizeof(TYPE); \
	\
	p = (TYPE *) buf; \
	for( i = 0; i < n_samples; i++ ) { \
		gint64 channel_sum; \
		int j; \
		\
		channel_sum = 0; \
		for( j = 0; j < channels; j++ ) \
			channel_sum += p[j]; \
		\
		p += channels; \
		sum += channel_sum * channel_sum; \
	} \
	\
	sum /= n_samples; \
}

/* Calculate root mean square as a percentage of the maximum value for this
 * depth. 
 */
int
rms( void *buf, size_t len, int sign, int depth, int rate, int channels )
{
	int i;
	guint64 sum;

	/*
	printf( "crms: buf = %p, len = %zd, sign = %d, depth = %d, "
		"rate = %d, channels = %d\n", 
		buf, len, sign, depth, rate, channels );
	 */

	/* Only support <1gb buffers.
	 */
	if( len > ((size_t) 1 << 30) )
		return( 0 );

	sum = 0;

	if( depth == 16 && sign )
		RMS( gint16 );
	if( depth == 32 && sign )
		RMS( gint32 );

	sum = sqrt( sum ); 

	return( sum );
}
