// Bounded desk check using the unmodified public NTIA LFMF API.
#include "LFMF.h"
#include <array>
#include <iomanip>
#include <iostream>
#include <string>

using ITS::Propagation::LFMF::LFMF;
using ITS::Propagation::LFMF::Result;

struct Ground { const char* name; double epsilon; double sigma; };

Result predict(double f, double d, const Ground& g, double htx=0.0,
               double hrx=0.0, double ptx=1000.0) {
    Result r{};
    const auto rc = LFMF(htx, hrx, f, ptx, 301.0, d,
                         g.epsilon, g.sigma, 1, r);
    if (rc != ITS::Propagation::LFMF::SUCCESS) {
        std::cerr << "LFMF error " << static_cast<int>(rc) << " at " << f
                  << " MHz, " << d << " km, " << g.name << "\n";
        std::exit(2);
    }
    return r;
}

double field(double f, double d, const Ground& g, double h=0.0) {
    return predict(f,d,g,h,h).E_dBuVm;
}

int main() {
    const std::array<Ground,3> gs{{
        {"dry",15.0,0.001}, {"wet",30.0,0.01}, {"sea",70.0,5.0}
    }};
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "NTIA LFMF v10 smooth-Earth vertical polarization; tx/rx=0m; "
                 "Pt=1kW; Ns=301; columns field dBuV/m\n";
    for (double f : {1.0, 30.0}) {
        for (double d : {1.0, 10.0, 100.0, 1000.0}) {
            if (f == 30.0 && d > 100.0) continue;
            for (const auto& g : gs)
                std::cout << "homogeneous f=" << f << " d=" << d << " ground="
                          << g.name << " E=" << field(f,d,g) << "\n";
        }
    }

    // Antenna-height sensitivity on the same sea path, for both bands.
    for (double f : {1.0,30.0}) {
        for (double d : {10.0,100.0}) {
            if (f == 30.0 && d > 100.0) continue;
            for (double h : {0.0,2.0,10.0,30.0}) {
                const auto r = predict(f,d,gs[2],h,h);
                std::cout << "geometry f=" << f << " d=" << d
                          << " sea equal_heights=" << h
                          << " E=" << r.E_dBuVm
                          << " Lb=" << r.A_btl__db
                          << " method=" << static_cast<int>(r.method) << "\n";
            }
        }
    }

    // Explicit 1 W same-ground 100 km link levels for the conditional
    // antenna-terminal C/N0 example in the chapter.
    for (double f : {1.0,30.0}) {
        const auto r = predict(f,100.0,gs[0],0.0,0.0,1.0);
        std::cout << "budget f=" << f << " d=100km ground=dry Pt=1W E="
                  << r.E_dBuVm << " P_rx=" << r.P_rx__dbm << " dBm\n";
    }

    // Land/sea sections. Compare both route orderings and boundary position.
    // Millington reciprocal result is the average of the forward and reverse
    // log-field estimates; each homogeneous E value uses the same LFMF inputs.
    const Ground land{"land",15.0,0.001}, sea{"sea",70.0,5.0};
    for (double f : {1.0,30.0}) {
        const double total = 100.0;
        for (double x : {10.0,50.0,90.0}) {
            const double y = total-x;
            const double Lx = field(f,x,land), Ltot = field(f,total,land);
            const double Sx = field(f,x,sea), Stot = field(f,total,sea);
            const double Ly = field(f,y,land), Sy = field(f,y,sea);
            const double landSea = Lx + Stot - Sx;
            const double seaLand = Sy + Ltot - Ly;
            std::cout << "mixed f=" << f << " path=" << x << "km-land+"
                      << y << "km-sea forward_E=" << landSea
                      << " reverse_E=" << seaLand
                      << " reciprocal_E=" << (landSea+seaLand)/2.0
                      << " directional_delta=" << (landSea-seaLand) << " dB\n";
        }
    }
}
