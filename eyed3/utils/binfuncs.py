################################################################################
#  Copyright (C) 2001  Ryan Finne <ryan@finnie.org>
#  Copyright (C) 2002-2011  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import struct

MAX_INT16 = (2 ** 16) // 2
MIN_INT16 = -(MAX_INT16 - 1)


def bytes2bin(bites, sz=8):
    """Accepts a string of ``bytes`` (chars) and returns an array of bits
    representing the bytes in big endian byte order. An optional max ``sz`` for
    each byte (default 8 bits/byte) which can  be used to mask out higher
    bits."""
    if sz < 1 or sz > 8:
        raise ValueError(f"Invalid sz value: {sz}")

    retval = []
    for b in [bytes([b]) for b in bites]:
        bits = []
        b = ord(b)
        while b > 0:
            bits.append(b & 1)
            b >>= 1

        if len(bits) < sz:
            bits.extend([0] * (sz - len(bits)))
        elif len(bits) > sz:
            bits = bits[:sz]

        # Big endian byte order.
        bits.reverse()
        retval.extend(bits)

    return retval


def bin2bytes(x):
    """Convert an array of bits (MSB first) into a string of characters."""
    bits = []
    bits.extend(x)
    bits.reverse()

    i = 0
    out = b''
    multi = 1
    ttl = 0
    for b in bits:
        i += 1
        ttl += b * multi
        multi *= 2
        if i == 8:
            i = 0
            out += bytes([ttl])
            multi = 1
            ttl = 0

    if multi > 1:
        out += bytes([ttl])

    out = bytearray(out)
    out.reverse()
    out = bytes(out)
    return out


def bin2dec(x):
    """Convert ``x``, an array of "bits" (MSB first), to it's decimal value."""
    bits = []
    bits.extend(x)
    bits.reverse()  # MSB

    multi = 1
    value = 0
    for b in bits:
        value += b * multi
        multi *= 2
    return value


def bytes2dec(bites, sz=8):
    return bin2dec(bytes2bin(bites, sz))


def dec2bin(n, p=1):
    """Convert a decimal value ``n`` to an array of bits (MSB first).
    Optionally, pad the overall size to ``p`` bits."""
    assert n >= 0
    if type(n) is not int:
        n = int(n)
    retval = []

    while n > 0:
        retval.append(n & 1)
        n >>= 1

    if p > 0:
        retval.extend([0] * (p - len(retval)))
    retval.reverse()
    return retval


def dec2bytes(n, p=1):
    return bin2bytes(dec2bin(n, p))


def bin2synchsafe(x):
    """Convert ``x``, a list of bits (MSB first), to a synch safe list of bits.
    (section 6.2 of the ID3 2.4 spec)."""
    n = bin2dec(x)
    if len(x) > 32 or n > 268435456:   # 2^28
        raise ValueError("Invalid value: %s" % str(x))
    elif len(x) < 8:
        return x

    bites = bytes([(n >> 21) & 0x7f,
                   (n >> 14) & 0x7f,
                   (n >> 7) & 0x7f,
                   (n >> 0) & 0x7f,
                   ])
    bits = bytes2bin(bites)
    assert(len(bits) == 32)

    return bits


def bytes2signedInt16(bites: bytes):
    if len(bites) != 2:
        raise ValueError("Signed 16 bit integer MUST be 2 bytes.")
    i = struct.unpack(">h", bites)
    return i[0]


def signedInt162bytes(n: int):
    n = int(n)
    if MIN_INT16 <= n <= MAX_INT16:
        return struct.pack(">h", n)
    raise ValueError(f"Signed int16 out of range: {n}")
