
#
# This file is part of LUNA.
#
# Copyright (c) 2020 Great Scott Gadgets <info@greatscottgadgets.com>
# SPDX-License-Identifier: BSD-3-Clause

""" TinyFPGA Platform definitions.

This is a non-core platform. To use it, you'll need to set your LUNA_PLATFORM variable:

    > export LUNA_PLATFORM="luna_boards.tangprimer20k:TangPrimer20kPlatform"
"""

import os
import subprocess

from amaranth import Elaboratable, ClockDomain, Module, ClockSignal, Instance, Signal, Const, ResetSignal
from amaranth.build import Resource, Subsignal, Pins, Attrs, Clock, Connector, PinsN
from amaranth_boards.tang_primer_20k import TangPrimer20kPlatform as _TangPrimer20kPlatform

from luna.gateware.platform.core import LUNAPlatform
from luna.gateware.architecture.car import PHYResetController

from amaranth_boards.resources import *


class TangPrimer20kDomainGenerator(Elaboratable):
    """ Creates clock domains for the Tang Primer. """

    def __init__(self, *, clock_frequencies=None, clock_signal_name=None):
        pass

    def elaborate(self, platform):
        m = Module()
        m.domains.sync   = ClockDomain()
        m.domains.usb    = ClockDomain()
        m.domains.normal    = ClockDomain()

        # ... create our 60 MHz IO and 120 MHz USB clock...
        clk = platform.request(platform.default_clk, dir="i")
        rst = platform.request("rst", dir="i")

        # We'll use our 48MHz clock for everything _except_ the usb domain...
        m.d.comb += [
            ClockSignal("sync").eq(ClockSignal("usb")),
            ResetSignal("sync").eq(~rst.i),
            ResetSignal("usb").eq(~rst.i),
            ClockSignal("normal").eq(clk.i),
            ResetSignal("normal").eq(~rst.i)
        ]

        return m


class TangPrimer20kPlatform(_TangPrimer20kPlatform, LUNAPlatform):  
    name                   = "Tang Primer 20k"
    device                 = "GW2N"
    clock_domain_generator = TangPrimer20kDomainGenerator
    default_usb_connection = "target_phy"
    default_clk = "clk27"


    resources   = [
            Resource("clk27", 0, Pins("H11", dir="i"),
                Clock(27e6), Attrs(IO_TYPE="LVCMOS33")),
            ULPIResource("target_phy", 0,
                data="G11 H12 J12 H13 T14 R13 P13 R12", clk="T15", clk_invert=True, clk_dir="i",
                dir="K12", nxt="K13", stp="K11", rst="F10", rst_invert=True, attrs=Attrs(IO_TYPE="LVCMOS33")),
            *LEDResources(pins="L16 L14 N14 N16", invert=True,
                attrs=Attrs(IO_TYPE="LVCMOS33")),
            Resource("rst",  0, Pins("C7"), Attrs(IO_TYPE="LVCMOS33")),
            #*ButtonResources(pins="C7", invert=True,
            #    attrs=Attrs(IO_TYPE="LVCMOS33"))
            ]



    def __init__(self):
        _TangPrimer20kPlatform.__init__(self,toolchain='Gowin')
        #LUNAPlatform.__init__(self)

