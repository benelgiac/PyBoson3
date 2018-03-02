#! /usr/bin/env python
# -*- coding: utf8 -*-
#
#    PyVisca-3 Implementation of the Boson commands in python3
#
#    Author: Giacomo Benelli benelli.giacomo@aerialtronics.com
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2 only.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#    USA

"""PyBoson-3 by Giacomo Benelli <benelli.giacomo@gmail.com>"""

import serial,sys
from _thread import allocate_lock
from .flirprotocols import Frame, Fbp, byteUnstuff, renderToByteArray
from time import sleep
import struct
from collections import OrderedDict

class BosonControl():
    
#const colormap_t colormap_rainbow = { {1, 3, 74, 0, 3, 74, 0, 3, 75, 0, 3, 75, 0, 3, 76, 0, 3, 76, 0, 3, 77, 0, 3, 79, 0, 3, 82, 0, 5, 85, 0, 7, 88, 0, 10, 91, 0, 14, 94, 0, 19, 98, 0, 22, 100, 0, 25, 103, 0, 28, 106, 0, 32, 109, 0, 35, 112, 0, 38, 116, 0, 40, 119, 0, 42, 123, 0, 45, 128, 0, 49, 133, 0, 50, 134, 0, 51, 136, 0, 52, 137, 0, 53, 139, 0, 54, 142, 0, 55, 144, 0, 56, 145, 0, 58, 149, 0, 61, 154, 0, 63, 156, 0, 65, 159, 0, 66, 161, 0, 68, 164, 0, 69, 167, 0, 71, 170, 0, 73, 174, 0, 75, 179, 0, 76, 181, 0, 78, 184, 0, 79, 187, 0, 80, 188, 0, 81, 190, 0, 84, 194, 0, 87, 198, 0, 88, 200, 0, 90, 203, 0, 92, 205, 0, 94, 207, 0, 94, 208, 0, 95, 209, 0, 96, 210, 0, 97, 211, 0, 99, 214, 0, 102, 217, 0, 103, 218, 0, 104, 219, 0, 105, 220, 0, 107, 221, 0, 109, 223, 0, 111, 223, 0, 113, 223, 0, 115, 222, 0, 117, 221, 0, 118, 220, 1, 120, 219, 1, 122, 217, 2, 124, 216, 2, 126, 214, 3, 129, 212, 3, 131, 207, 4, 132, 205, 4, 133, 202, 4, 134, 197, 5, 136, 192, 6, 138, 185, 7, 141, 178, 8, 142, 172, 10, 144, 166, 10, 144, 162, 11, 145, 158, 12, 146, 153, 13, 147, 149, 15, 149, 140, 17, 151, 132, 22, 153, 120, 25, 154, 115, 28, 156, 109, 34, 158, 101, 40, 160, 94, 45, 162, 86, 51, 164, 79, 59, 167, 69, 67, 171, 60, 72, 173, 54, 78, 175, 48, 83, 177, 43, 89, 179, 39, 93, 181, 35, 98, 183, 31, 105, 185, 26, 109, 187, 23, 113, 188, 21, 118, 189, 19, 123, 191, 17, 128, 193, 14, 134, 195, 12, 138, 196, 10, 142, 197, 8, 146, 198, 6, 151, 200, 5, 155, 201, 4, 160, 203, 3, 164, 204, 2, 169, 205, 2, 173, 206, 1, 175, 207, 1, 178, 207, 1, 184, 208, 0, 190, 210, 0, 193, 211, 0, 196, 212, 0, 199, 212, 0, 202, 213, 1, 207, 214, 2, 212, 215, 3, 215, 214, 3, 218, 214, 3, 220, 213, 3, 222, 213, 4, 224, 212, 4, 225, 212, 5, 226, 212, 5, 229, 211, 5, 232, 211, 6, 232, 211, 6, 233, 211, 6, 234, 210, 6, 235, 210, 7, 236, 209, 7, 237, 208, 8, 239, 206, 8, 241, 204, 9, 242, 203, 9, 244, 202, 10, 244, 201, 10, 245, 200, 10, 245, 199, 11, 246, 198, 11, 247, 197, 12, 248, 194, 13, 249, 191, 14, 250, 189, 14, 251, 187, 15, 251, 185, 16, 252, 183, 17, 252, 178, 18, 253, 174, 19, 253, 171, 19, 254, 168, 20, 254, 165, 21, 254, 164, 21, 255, 163, 22, 255, 161, 22, 255, 159, 23, 255, 157, 23, 255, 155, 24, 255, 149, 25, 255, 143, 27, 255, 139, 28, 255, 135, 30, 255, 131, 31, 255, 127, 32, 255, 118, 34, 255, 110, 36, 255, 104, 37, 255, 101, 38, 255, 99, 39, 255, 93, 40, 255, 88, 42, 254, 82, 43, 254, 77, 45, 254, 69, 47, 254, 62, 49, 253, 57, 50, 253, 53, 52, 252, 49, 53, 252, 45, 55, 251, 39, 57, 251, 33, 59, 251, 32, 60, 251, 31, 60, 251, 30, 61, 251, 29, 61, 251, 28, 62, 250, 27, 63, 250, 27, 65, 249, 26, 66, 249, 26, 68, 248, 25, 70, 248, 24, 73, 247, 24, 75, 247, 25, 77, 247, 25, 79, 247, 26, 81, 247, 32, 83, 247, 35, 85, 247, 38, 86, 247, 42, 88, 247, 46, 90, 247, 50, 92, 248, 55, 94, 248, 59, 96, 248, 64, 98, 248, 72, 101, 249, 81, 104, 249, 87, 106, 250, 93, 108, 250, 95, 109, 250, 98, 110, 250, 100, 111, 251, 101, 112, 251, 102, 113, 251, 109, 117, 252, 116, 121, 252, 121, 123, 253, 126, 126, 253, 130, 128, 254, 135, 131, 254, 139, 133, 254, 144, 136, 254, 151, 140, 255, 158, 144, 255, 163, 146, 255, 168, 149, 255, 173, 152, 255, 176, 153, 255, 178, 155, 255, 184, 160, 255, 191, 165, 255, 195, 168, 255, 199, 172, 255, 203, 175, 255, 207, 179, 255, 211, 182, 255, 216, 185, 255, 218, 190, 255, 220, 196, 255, 222, 200, 255, 225, 202, 255, 227, 204, 255, 230, 206, 255, 233, 208} };

#const colormap_t colormap_grayscale = { {0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 15, 15, 15, 16, 16, 16, 17, 17, 17, 18, 18, 18, 19, 19, 19, 20, 20, 20, 21, 21, 21, 22, 22, 22, 23, 23, 23, 24, 24, 24, 25, 25, 25, 26, 26, 26, 27, 27, 27, 28, 28, 28, 29, 29, 29, 30, 30, 30, 31, 31, 31, 32, 32, 32, 33, 33, 33, 34, 34, 34, 35, 35, 35, 36, 36, 36, 37, 37, 37, 38, 38, 38, 39, 39, 39, 40, 40, 40, 41, 41, 41, 42, 42, 42, 43, 43, 43, 44, 44, 44, 45, 45, 45, 46, 46, 46, 47, 47, 47, 48, 48, 48, 49, 49, 49, 50, 50, 50, 51, 51, 51, 52, 52, 52, 53, 53, 53, 54, 54, 54, 55, 55, 55, 56, 56, 56, 57, 57, 57, 58, 58, 58, 59, 59, 59, 60, 60, 60, 61, 61, 61, 62, 62, 62, 63, 63, 63, 64, 64, 64, 65, 65, 65, 66, 66, 66, 67, 67, 67, 68, 68, 68, 69, 69, 69, 70, 70, 70, 71, 71, 71, 72, 72, 72, 73, 73, 73, 74, 74, 74, 75, 75, 75, 76, 76, 76, 77, 77, 77, 78, 78, 78, 79, 79, 79, 80, 80, 80, 81, 81, 81, 82, 82, 82, 83, 83, 83, 84, 84, 84, 85, 85, 85, 86, 86, 86, 87, 87, 87, 88, 88, 88, 89, 89, 89, 90, 90, 90, 91, 91, 91, 92, 92, 92, 93, 93, 93, 94, 94, 94, 95, 95, 95, 96, 96, 96, 97, 97, 97, 98, 98, 98, 99, 99, 99, 100, 100, 100, 101, 101, 101, 102, 102, 102, 103, 103, 103, 104, 104, 104, 105, 105, 105, 106, 106, 106, 107, 107, 107, 108, 108, 108, 109, 109, 109, 110, 110, 110, 111, 111, 111, 112, 112, 112, 113, 113, 113, 114, 114, 114, 115, 115, 115, 116, 116, 116, 117, 117, 117, 118, 118, 118, 119, 119, 119, 120, 120, 120, 121, 121, 121, 122, 122, 122, 123, 123, 123, 124, 124, 124, 125, 125, 125, 126, 126, 126, 127, 127, 127, 128, 128, 128, 129, 129, 129, 130, 130, 130, 131, 131, 131, 132, 132, 132, 133, 133, 133, 134, 134, 134, 135, 135, 135, 136, 136, 136, 137, 137, 137, 138, 138, 138, 139, 139, 139, 140, 140, 140, 141, 141, 141, 142, 142, 142, 143, 143, 143, 144, 144, 144, 145, 145, 145, 146, 146, 146, 147, 147, 147, 148, 148, 148, 149, 149, 149, 150, 150, 150, 151, 151, 151, 152, 152, 152, 153, 153, 153, 154, 154, 154, 155, 155, 155, 156, 156, 156, 157, 157, 157, 158, 158, 158, 159, 159, 159, 160, 160, 160, 161, 161, 161, 162, 162, 162, 163, 163, 163, 164, 164, 164, 165, 165, 165, 166, 166, 166, 167, 167, 167, 168, 168, 168, 169, 169, 169, 170, 170, 170, 171, 171, 171, 172, 172, 172, 173, 173, 173, 174, 174, 174, 175, 175, 175, 176, 176, 176, 177, 177, 177, 178, 178, 178, 179, 179, 179, 180, 180, 180, 181, 181, 181, 182, 182, 182, 183, 183, 183, 184, 184, 184, 185, 185, 185, 186, 186, 186, 187, 187, 187, 188, 188, 188, 189, 189, 189, 190, 190, 190, 191, 191, 191, 192, 192, 192, 193, 193, 193, 194, 194, 194, 195, 195, 195, 196, 196, 196, 197, 197, 197, 198, 198, 198, 199, 199, 199, 200, 200, 200, 201, 201, 201, 202, 202, 202, 203, 203, 203, 204, 204, 204, 205, 205, 205, 206, 206, 206, 207, 207, 207, 208, 208, 208, 209, 209, 209, 210, 210, 210, 211, 211, 211, 212, 212, 212, 213, 213, 213, 214, 214, 214, 215, 215, 215, 216, 216, 216, 217, 217, 217, 218, 218, 218, 219, 219, 219, 220, 220, 220, 221, 221, 221, 222, 222, 222, 223, 223, 223, 224, 224, 224, 225, 225, 225, 226, 226, 226, 227, 227, 227, 228, 228, 228, 229, 229, 229, 230, 230, 230, 231, 231, 231, 232, 232, 232, 233, 233, 233, 234, 234, 234, 235, 235, 235, 236, 236, 236, 237, 237, 237, 238, 238, 238, 239, 239, 239, 240, 240, 240, 241, 241, 241, 242, 242, 242, 243, 243, 243, 244, 244, 244, 245, 245, 245, 246, 246, 246, 247, 247, 247, 248, 248, 248, 249, 249, 249, 250, 250, 250, 251, 251, 251, 252, 252, 252, 253, 253, 253, 254, 254, 254, 255, 255, 255} };

#const colormap_t colormap_ironblack = { {255, 255, 255, 253, 253, 253, 251, 251, 251, 249, 249, 249, 247, 247, 247, 245, 245, 245, 243, 243, 243, 241, 241, 241, 239, 239, 239, 237, 237, 237, 235, 235, 235, 233, 233, 233, 231, 231, 231, 229, 229, 229, 227, 227, 227, 225, 225, 225, 223, 223, 223, 221, 221, 221, 219, 219, 219, 217, 217, 217, 215, 215, 215, 213, 213, 213, 211, 211, 211, 209, 209, 209, 207, 207, 207, 205, 205, 205, 203, 203, 203, 201, 201, 201, 199, 199, 199, 197, 197, 197, 195, 195, 195, 193, 193, 193, 191, 191, 191, 189, 189, 189, 187, 187, 187, 185, 185, 185, 183, 183, 183, 181, 181, 181, 179, 179, 179, 177, 177, 177, 175, 175, 175, 173, 173, 173, 171, 171, 171, 169, 169, 169, 167, 167, 167, 165, 165, 165, 163, 163, 163, 161, 161, 161, 159, 159, 159, 157, 157, 157, 155, 155, 155, 153, 153, 153, 151, 151, 151, 149, 149, 149, 147, 147, 147, 145, 145, 145, 143, 143, 143, 141, 141, 141, 139, 139, 139, 137, 137, 137, 135, 135, 135, 133, 133, 133, 131, 131, 131, 129, 129, 129, 126, 126, 126, 124, 124, 124, 122, 122, 122, 120, 120, 120, 118, 118, 118, 116, 116, 116, 114, 114, 114, 112, 112, 112, 110, 110, 110, 108, 108, 108, 106, 106, 106, 104, 104, 104, 102, 102, 102, 100, 100, 100, 98, 98, 98, 96, 96, 96, 94, 94, 94, 92, 92, 92, 90, 90, 90, 88, 88, 88, 86, 86, 86, 84, 84, 84, 82, 82, 82, 80, 80, 80, 78, 78, 78, 76, 76, 76, 74, 74, 74, 72, 72, 72, 70, 70, 70, 68, 68, 68, 66, 66, 66, 64, 64, 64, 62, 62, 62, 60, 60, 60, 58, 58, 58, 56, 56, 56, 54, 54, 54, 52, 52, 52, 50, 50, 50, 48, 48, 48, 46, 46, 46, 44, 44, 44, 42, 42, 42, 40, 40, 40, 38, 38, 38, 36, 36, 36, 34, 34, 34, 32, 32, 32, 30, 30, 30, 28, 28, 28, 26, 26, 26, 24, 24, 24, 22, 22, 22, 20, 20, 20, 18, 18, 18, 16, 16, 16, 14, 14, 14, 12, 12, 12, 10, 10, 10, 8, 8, 8, 6, 6, 6, 4, 4, 4, 2, 2, 2, 0, 0, 0, 0, 0, 9, 2, 0, 16, 4, 0, 24, 6, 0, 31, 8, 0, 38, 10, 0, 45, 12, 0, 53, 14, 0, 60, 17, 0, 67, 19, 0, 74, 21, 0, 82, 23, 0, 89, 25, 0, 96, 27, 0, 103, 29, 0, 111, 31, 0, 118, 36, 0, 120, 41, 0, 121, 46, 0, 122, 51, 0, 123, 56, 0, 124, 61, 0, 125, 66, 0, 126, 71, 0, 127, 76, 1, 128, 81, 1, 129, 86, 1, 130, 91, 1, 131, 96, 1, 132, 101, 1, 133, 106, 1, 134, 111, 1, 135, 116, 1, 136, 121, 1, 136, 125, 2, 137, 130, 2, 137, 135, 3, 137, 139, 3, 138, 144, 3, 138, 149, 4, 138, 153, 4, 139, 158, 5, 139, 163, 5, 139, 167, 5, 140, 172, 6, 140, 177, 6, 140, 181, 7, 141, 186, 7, 141, 189, 10, 137, 191, 13, 132, 194, 16, 127, 196, 19, 121, 198, 22, 116, 200, 25, 111, 203, 28, 106, 205, 31, 101, 207, 34, 95, 209, 37, 90, 212, 40, 85, 214, 43, 80, 216, 46, 75, 218, 49, 69, 221, 52, 64, 223, 55, 59, 224, 57, 49, 225, 60, 47, 226, 64, 44, 227, 67, 42, 228, 71, 39, 229, 74, 37, 230, 78, 34, 231, 81, 32, 231, 85, 29, 232, 88, 27, 233, 92, 24, 234, 95, 22, 235, 99, 19, 236, 102, 17, 237, 106, 14, 238, 109, 12, 239, 112, 12, 240, 116, 12, 240, 119, 12, 241, 123, 12, 241, 127, 12, 242, 130, 12, 242, 134, 12, 243, 138, 12, 243, 141, 13, 244, 145, 13, 244, 149, 13, 245, 152, 13, 245, 156, 13, 246, 160, 13, 246, 163, 13, 247, 167, 13, 247, 171, 13, 248, 175, 14, 248, 178, 15, 249, 182, 16, 249, 185, 18, 250, 189, 19, 250, 192, 20, 251, 196, 21, 251, 199, 22, 252, 203, 23, 252, 206, 24, 253, 210, 25, 253, 213, 27, 254, 217, 28, 254, 220, 29, 255, 224, 30, 255, 227, 39, 255, 229, 53, 255, 231, 67, 255, 233, 81, 255, 234, 95, 255, 236, 109, 255, 238, 123, 255, 240, 137, 255, 242, 151, 255, 244, 165, 255, 246, 179, 255, 248, 193, 255, 249, 207, 255, 251, 221, 255, 253, 235, 255, 255, 24} };
        
    # Format: Command Hex Code, Byte Size (command, response, get, set)
    COMMANDS = {
        'GETSERIAL'           :    { 'id': bytearray([0x00, 0x05, 0x00, 0x02]), 'retbytes': 4},
        'GETCOLORLUT'         :    { 'id': bytearray([0x00, 0x0B, 0x00, 0x04]), 'retbytes': 4, 'type': 'int'},
        'SETCOLORLUT'         :    { 'id': bytearray([0x00, 0x0B, 0x00, 0x03]), 'retbytes': 0},
        'COLORLUTSETCONTROL'  :    { 'id': bytearray([0x00, 0x0B, 0x00, 0x01]), 'retbytes': 0},
        'COLORLUTGETCONTROL'  :    { 'id': bytearray([0x00, 0x0B, 0x00, 0x02]), 'retbytes': 4, 'type': 'int'},
        'GETPARTNUMBER'       :    { 'id': bytearray([0x00, 0x05, 0x00, 0x04]), 'retbytes': 20},
        'GETGAINMODE'         :    { 'id': bytearray([0x00, 0x05, 0x00, 0x15]), 'retbytes': 4, 'type': 'int'},
        'SETGAINMODE'         :    { 'id': bytearray([0x00, 0x05, 0x00, 0x14]), 'retbytes': 0},
        'ACGSETLINEARPERCENT' :    { 'id': bytearray([0x00, 0x09, 0x00, 0x03]), 'retbytes': 0},
        'ACGGETLINEARPERCENT' :    { 'id': bytearray([0x00, 0x09, 0x00, 0x04]), 'retbytes': 4, 'type': 'float'},
        'ACGGETOUTLIERCUT'    :    { 'id': bytearray([0x00, 0x09, 0x00, 0x06]), 'retbytes': 4, 'type': 'float'},
        'ACGSETOUTLIERCUT'    :    { 'id': bytearray([0x00, 0x09, 0x00, 0x05]), 'retbytes': 0},
        'ACGGETMAXGAIN'       :    { 'id': bytearray([0x00, 0x09, 0x00, 0x0A]), 'retbytes': 4, 'type': 'float'},
        'ACGSETMAXGAIN'       :    { 'id': bytearray([0x00, 0x09, 0x00, 0x09]), 'retbytes': 0},
        'ACGGETDUMPINGFACTOR' :    { 'id': bytearray([0x00, 0x09, 0x00, 0x0C]), 'retbytes': 4, 'type': 'float'},
        'ACGSETDUMPINGFACTOR' :    { 'id': bytearray([0x00, 0x09, 0x00, 0x0B]), 'retbytes': 0},
        'ACGGETGAMMA'         :    { 'id': bytearray([0x00, 0x09, 0x00, 0x0E]), 'retbytes': 4, 'type': 'float'},
        'ACGSETGAMMA'         :    { 'id': bytearray([0x00, 0x09, 0x00, 0x0D]), 'retbytes': 0},
        'ACGGETDTBR'          :    { 'id': bytearray([0x00, 0x09, 0x00, 0x16]), 'retbytes': 4, 'type': 'float'},
        'ACGSETDTBR'          :    { 'id': bytearray([0x00, 0x09, 0x00, 0x15]), 'retbytes': 0},
        'ACGGETSIGMAR'        :    { 'id': bytearray([0x00, 0x09, 0x00, 0x18]), 'retbytes': 4, 'type': 'float'},
        'ACGSETSIGMAR'        :    { 'id': bytearray([0x00, 0x09, 0x00, 0x17]), 'retbytes': 0},
        'ACGGETENTROPY'       :    { 'id': bytearray([0x00, 0x09, 0x00, 0x1F]), 'retbytes': 4, 'type': 'int'},
        'ACGSETENTROPY'       :    { 'id': bytearray([0x00, 0x09, 0x00, 0x1E]), 'retbytes': 0},
        'ACGRESTOREDEFAULT'   :    { 'id': bytearray([0x00, 0x05, 0x00, 0x1B]), 'retbytes': 0},
        'FPATEMPDEDCx10'      :    { 'id': bytearray([0x00, 0x05, 0x00, 0x30]), 'retbytes': 2, 'type': 'short'},
        'FPAGETTEMPTABLE'     :    { 'id': bytearray([0x00, 0x02, 0x00, 0x20]), 'retbytes': 64},
        'SCALERGETZOOM'       :    { 'id': bytearray([0x00, 0x0D, 0x00, 0x03]), 'retbytes': 12},
        'SCALERGETMAXZOOM'    :    { 'id': bytearray([0x00, 0x0D, 0x00, 0x03]), 'retbytes': 4, 'type': 'int' },
        'GETSWVERSION'        :    { 'id': bytearray([0x00, 0x05, 0x00, 0x56]), 'retbytes': 12},
        'SCALERSETZOOM'       :    { 'id': bytearray([0x00, 0x0D, 0x00, 0x02]), 'retbytes': 0},
    }
    
    LUT = OrderedDict([
        (0x00000000   , 'WHITEHOT'),
        (0x00000001   , 'BLACKHOT'),
        (0x00000002   , 'RAINBOW'),
        (0x00000003   , 'RAINBOW_HC'),
        (0x00000004   , 'IRONBOW'),
        (0x00000005   , 'LAVA'),
        (0x00000006   , 'ARCTIC'),
        (0x00000007   , 'GLOBOW'),
        (0x00000008   , 'GRADEDFIRE'),
        (0x00000009   , 'HOTTEST'),
    ])
    
    GAINMODE = OrderedDict([
        (0x00000000   , 'HIGH GAIN'),
        (0x00000001   , 'LOW GAIN'),
        (0x00000002   , 'AUTO GAIN'),
        (0x00000003   , 'DUAL GAIN'),
        (0x00000004   , 'MANUAL GAIN'),
    ])
    
    FLR_ENABLE_E=OrderedDict([
        (0x00000001   , 'TRUE'),
        (0x00000000   , 'FALSE'),
    ])
    
    _lutstring = ''
    
    class SCALER_ZOOM_PARAMS ():
        
        fields = OrderedDict([
            ('zoom'      , 0x00000000),
            ('xCenter'   , 0x00000000),
            ('yCenter'   , 0x00000000),
        ])
        def toByteArray(self):
            return bytearray(struct.pack('>i',self.fields['zoom']))+ \
            bytearray(struct.pack('>i',self.fields['xCenter']))+ \
            bytearray(struct.pack('>i',self.fields['yCenter']))
        
        #This needs to work on UNSTUFFED byte array
        def fromByteArray(self, ba):
            assert (len(ba)==12)
            self.fields['zoom'] = struct.unpack('>i',ba[0:4])[0]
            self.fields['xCenter'] = struct.unpack('>i',ba[4:8])[0]
            self.fields['yCenter'] = struct.unpack('>i',ba[8:12])[0]
            
    __instance = None
    started = False
    def __new__(cls):
        if BosonControl.__instance is None:
            BosonControl.__instance = object.__new__(cls)
        return BosonControl.__instance

    #---------- Methods related to serial port handling ---------------
    def __init__(self,portname="/dev/ttyACM0", timeout=1):
        #This may give concurrency problems
        if self.started: return

        self.serialport=None
        self.mutex = allocate_lock()
        self.portname=portname
        self.open_port(timeout)
        self.started= True

    def open_port(self, timeout):

        self.mutex.acquire()

        if (self.serialport == None):
            try:
                self.serialport = serial.Serial(self.portname,921600,timeout=timeout,stopbits=1,bytesize=8,rtscts=False, dsrdtr=False)
                self.serialport.flushInput()
            except Exception as e:
                print ("Exception opening serial port '%s' for display: %s\n" % (self.portname,e))
                raise e
                self.serialport = None
        
        self.serialport.reset_input_buffer()
        self.serialport.reset_output_buffer()

        self.mutex.release()

    def dump(self,packet,title=None):
        if not packet or len(packet)==0:
            return

        print ('%s: %s' % (title,packet))


    def recv_packet(self,extra_title=None):
        # read up to 32 bytes until 0xff
        packet=b''
        count=0
        while count<128:
            s=self.serialport.read(1)
            if s:
                count+=1
                packet=packet+bytes(s)
            else:
                import pdb;pdb.set_trace()
                print ("ERROR: Timeout waiting for reply")
                break
            if s==b'\xae':
                break

        if extra_title:
            self.dump(packet,"recv: %s" % extra_title)
        else:
            self.dump(packet,"recv")
        return packet

    def _write_packet(self,packet):

        if not self.serialport.isOpen():
            sys.exit(1)

        # lets see if a completion message or someting
        # else waits in the buffer. If yes dump it.
        if self.serialport.inWaiting():
            self.recv_packet("ignored")

        self.dump (packet, 'Sending packet')
        self.serialport.write(packet)
        
    def send_packet(self, packet):

        self.mutex.acquire()

        self._write_packet(packet)

        reply = self.recv_packet()

        self.mutex.release()

        return reply
    
    #---------- Using Frame and Fbp to assemble packet ---------------
    def _construct_cmd(self, _command_name, _data = bytearray()):
        payload = Fbp(self.COMMANDS[_command_name]['id'], _data)
        
        frame = Frame(payload.raw())
        
        serial_cmd = frame.raw()
        return serial_cmd
        
    ####### Poor man's data extractor. reply must be unstuffed please##
    def getDataFromReply(self, reply, commandname):
        _type = None
        length = self.COMMANDS[commandname]['retbytes']
        if 'type' in self.COMMANDS[commandname]:
            _type = self.COMMANDS[commandname]['type']
        
        end = -3
        start = end-length
        status = start - 4
        print ('Command status is %s' % reply[status:start])
        if _type == 'int':
            return struct.unpack('>i',reply[start:end])[0]
        elif _type == 'float':
            return struct.unpack('>f',reply[start:end])[0]
        elif _type == 'short':
            return struct.unpack('>h',reply[start:end])[0]
        else:
            return reply[start:end]
    
    def sendCmdAndGetReply(self, commandname, data = bytearray()):
        retdata = b''
        reply = byteUnstuff(self.send_packet(self._construct_cmd(commandname, data)))
        if self.COMMANDS[commandname]['retbytes']==4:
             retdata = self.getDataFromReply(reply, commandname)
        #elif self.COMMANDS[commandname]['retbytes']!=0:
        else:
             retdata = self.getDataFromReply(reply, commandname)

        #import pdb;pdb.set_trace()
        return retdata

    #---------- Methods supposed to be invoked from users --------------
    def getSerial(self):
        return self.sendCmdAndGetReply('GETSERIAL')
    
    def getColorLut(self):
        color_enabled = self.sendCmdAndGetReply('COLORLUTGETCONTROL')
        if not color_enabled:
            self._lutstring == 'GREYSCALE'
            return 'GREYSCALE'
        else:
            return self.LUT[self.sendCmdAndGetReply('GETCOLORLUT')]
        
    def getPartNumber(self):
        return self.sendCmdAndGetReply('GETPARTNUMBER')
        
    def setColorLut(self, lutstring):
        if lutstring == 'GREYSCALE':
            self._lutstring = 'GREYSCALE'
            return self.sendCmdAndGetReply('COLORLUTSETCONTROL', ToByteArray(_getKeyFromValue(self.FLR_ENABLE_E,'FALSE')))
        else:
            self._lutstring = lutstring
            self.sendCmdAndGetReply('COLORLUTSETCONTROL', ToByteArray(_getKeyFromValue(self.FLR_ENABLE_E,'TRUE')))
            return self.sendCmdAndGetReply('SETCOLORLUT', ToByteArray(_getKeyFromValue(self.LUT, lutstring)))
        
    def getGainState(self):
        return self.GAINMODE[self.sendCmdAndGetReply('GETGAINMODE')]
        
    def setGainState(self, gainstring):
        return self.sendCmdAndGetReply('SETGAINMODE', ToByteArray(_getKeyFromValue(self.GAINMODE, gainstring)))
        
    def getAgcLinearPercent(self):
        return self.sendCmdAndGetReply('ACGGETLINEARPERCENT')
    
    def getAgcOutlierCut(self):
        return self.sendCmdAndGetReply('ACGGETOUTLIERCUT')    

    def getAgcMaxGain(self):
        return self.sendCmdAndGetReply('ACGGETMAXGAIN')        
        
    def setAgcMaxGain(self, value):
        return self.sendCmdAndGetReply('ACGSETMAXGAIN', ToByteArray(value))
        
    def setLinearPercent(self, value):
        return self.sendCmdAndGetReply('ACGSETLINEARPERCENT', ToByteArray(value))
        
    def setOutlierCut(self, value):
        return self.sendCmdAndGetReply('ACGSETOUTLIERCUT', ToByteArray(value))
        
    def restoreDefaults(self):
        return self.sendCmdAndGetReply('ACGRESTOREDEFAULT')
        
    def setAgcDumpingFactor(self, value):
        return self.sendCmdAndGetReply('ACGSETDUMPINGFACTOR', ToByteArray(value))
        
    def getAgcDumpingFactor(self):
        return self.sendCmdAndGetReply('ACGGETDUMPINGFACTOR')
        
    def setAgcGamma(self,value):
        return self.sendCmdAndGetReply('ACGSETGAMMA', ToByteArray(value))
        
    def getAgcGamma(self):
        return self.sendCmdAndGetReply('ACGGETGAMMA')
        
    def setAgcDtbr(self,value):
        return self.sendCmdAndGetReply('ACGSETDTBR', ToByteArray(value))
        
    def getAgcDtbr(self):
        return self.sendCmdAndGetReply('ACGGETDTBR')
        
    def setAgcSigmar(self,value):
        return self.sendCmdAndGetReply('ACGSETSIGMAR', ToByteArray(value))
        
    def getAgcSigmar(self):
        return self.sendCmdAndGetReply('ACGGETSIGMAR')
        
    def getSwVersion(self):
        #This is cheating. It's Michele's fault :)
        sv = self.SCALER_ZOOM_PARAMS()
        sv.fromByteArray(self.sendCmdAndGetReply('GETSWVERSION'))
        major = sv.fields['zoom']
        minor = sv.fields['xCenter']
        patch = sv.fields['yCenter']
        print ('SW version is %d.%d.%d' %(major, minor, patch))
        
                
    def getFpaTempTable(self):
        fpa_temp_table = self.sendCmdAndGetReply('FPAGETTEMPTABLE')
        #print('stuffed packet is %s' % fpa_temp_table)
        #print('unstuffed packet is %s' % byteUnstuff(fpa_temp_table))
        #print('table array is %s' % )
        temparray = FpaTableToIntArray(byteUnstuff(fpa_temp_table))
        return min(temparray), max(temparray)
        
    def setEntropy(self,value):
        if value:
            self.sendCmdAndGetReply('ACGSETENTROPY', ToByteArray(_getKeyFromValue(self.FLR_ENABLE_E,'TRUE')))
        else:
            self.sendCmdAndGetReply('ACGSETENTROPY', ToByteArray(_getKeyFromValue(self.FLR_ENABLE_E,'FALSE')))
        
    def getEntropy(self):
        retval = self.sendCmdAndGetReply('ACGGETENTROPY')
        if retval == 1:
            return True
        elif retval == 0:
            return False
        else:
            assert(True)
            
    def getScalerZoom(self):
        zoom_params = self.SCALER_ZOOM_PARAMS()
        zoom_params.fromByteArray(self.sendCmdAndGetReply('SCALERGETZOOM'))
        return zoom_params.fields['zoom']
        
    def setScalerZoom(self,value):
        #Know what is the max you can set and exit if necessary
        max_zoom = self.sendCmdAndGetReply('SCALERGETMAXZOOM')
        print ('Max Zoom is %s' % max_zoom)
        if (value > max_zoom):
            return
        
        #Get Current Zoom parameters    
        zoom_params = self.SCALER_ZOOM_PARAMS()
        zoom_params.fromByteArray(self.sendCmdAndGetReply('SCALERGETZOOM'))
        
        #Alter Zoom level only
        zoom_params.fields['zoom'] = value
        
        return self.sendCmdAndGetReply('SCALERSETZOOM', zoom_params.toByteArray())
        
    def test_LUT(self):
        print ('Part number is %s' % self.getPartNumber())
        sleep(1)

        for data , lutstring in self.LUT.items():
            self.setColorLut(lutstring)
            sleep(1)
            print ('LUT is %s' % self.getColorLut())
            sleep(1)
        return 

#---------- Utility functions ---------------
def _getKeyFromValue(_d, _value):
    for k,v in _d.items():
        if v==_value:
            return k
    return None

def ToByteArray(_i):
    frmt = ''
    if isinstance(_i, int):
        frmt = '>i'
    elif isinstance(_i, float):
        frmt = '>f'
    else:
        assert(True)
    
    return struct.pack(frmt,_i)
    
def FpaTableToIntArray(table):
    skipme=False
    arr=[]
    for pos in range(0, len(table)-1):
        if not skipme:
            twobytes = table[pos: pos+2]
            arr.append(struct.unpack('>h',twobytes)[0])
            skipme=True
        else:
            skipme=False
    return arr
    
