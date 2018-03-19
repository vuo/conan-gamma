#include <stdio.h>
#include <Gamma/Oscillator.h>
#include <Gamma/Sync.h>

int main()
{
	gam::Sync sync(11025);
	gam::Sine<> sine;
	sync << sine;
	sine.freq(1378);
	printf("Successfully initialized Gamma.  First few sine values: %g %g %g %g\n", sine(), sine(), sine(), sine());
	return 0;
}
