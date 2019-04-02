#!/usr/bin/env python3
# coding=utf-8
"""
 *
 * by Wenger Florian 2015-09-02
 * wenger@unifox.at
 *
 * endless loop (until ctrl+c) displays measurement from SMA Energymeter
 *
 *
 *  this software is released under GNU General Public License, version 2.
 *  This program is free software;
 *  you can redistribute it and/or modify it under the terms of the GNU General Public License
 *  as published by the Free Software Foundation; version 2 of the License.
 *  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 *  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *  See the GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License along with this program;
 *  if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * 2018-12-22 Tommi2Day small enhancements
 *
 */
"""

import signal
import sys
import smaem
import socket
import struct
from configparser import ConfigParser

# clean exit
def abortprogram(signal,frame):
    # Housekeeping -> nothing to cleanup
    print('STRG + C = end program')
    sys.exit(0)

# abort-signal
signal.signal(signal.SIGINT, abortprogram)

# listen to the Multicast; SMA-Energymeter sends its measurements to 239.12.255.254:9522

#read configuration
parser = ConfigParser()
#alternate config locations
parser.read(['/etc/smaemd/config','config'])
try:
    smaemserials=parser.get('SMA-EM', 'serials')
except:
    print('Cannot find base config entry SMA-EM serials')
    sys.exit(1)

serials=smaemserials.split(' ')
#smavalues=parser.get('SMA-EM', 'values')
#values=smavalues.split(' ')
pidfile=parser.get('DAEMON', 'pidfile')
ipbind=parser.get('DAEMON', 'ipbind')
MCAST_GRP = parser.get('DAEMON', 'mcastgrp')
MCAST_PORT = int(parser.get('DAEMON', 'mcastport'))

if MCAST_GRP == "":
    MCAST_GRP = '239.12.255.254'
if MCAST_PORT == 0:
    MCAST_PORT = 9522

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))
try:
    mreq = struct.pack("4s4s", socket.inet_aton(MCAST_GRP), socket.inet_aton(ipbind))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
except BaseException:
    print('could not connect to mulicast group or bind to given interface')
    sys.exit(1)
# processing received messages
while True:
  emparts = {}
  emparts=smaem.readem(sock)
  #
  # Output...
  # don't know what P,Q and S means:
  # http://en.wikipedia.org/wiki/AC_power or http://de.wikipedia.org/wiki/Scheinleistung
  # thd = Total_Harmonic_Distortion http://de.wikipedia.org/wiki/Total_Harmonic_Distortion
  # cos phi is always positive, no matter what quadrant
  print ('\n')
  print ('SMA-EM Serial:{}'.format(emparts['serial']))
  print ('----sum----')
  print ('P: consume:{}W {}kWh supply:{}W {}kWh'.format(emparts['pconsume'],emparts['pconsumecounter'],emparts['psupply'],emparts['psupplycounter']))
  print ('S: consume:{}VA {}kVAh supply:{}VA {}VAh'.format(emparts['sconsume'],emparts['sconsumecounter'],emparts['ssupply'],emparts['ssupplycounter']))
  print ('Q: cap {}var {}kvarh ind {}var {}kvarh'.format(emparts['qconsume'],emparts['qconsumecounter'],emparts['qsupply'],emparts['qsupplycounter']))
  print ('cos phi:{}°'.format(emparts['cosphi']))
  print ('----L1----')
  print ('P: consume:{}W {}kWh supply:{}W {}kWh'.format(emparts['p1consume'],emparts['p1consumecounter'],emparts['p1supply'],emparts['p1supplycounter']))
  print ('S: consume:{}VA {}kVAh supply:{}VA {}kVAh'.format(emparts['s1consume'],emparts['s1consumecounter'],emparts['s1supply'],emparts['s1supplycounter']))
  print ('Q: cap {}var {}kvarh ind {}var {}kvarh'.format(emparts['q1consume'],emparts['q1consumecounter'],emparts['q1supply'],emparts['q1supplycounter']))
  print ('U: {}V thd:{}% cos phi:{}°'.format(emparts['v1'],emparts['thd1'],emparts['cosphi1']))
  print ('----L2----')
  print ('P: consume:{}W {}kWh supply:{}W {}kWh'.format(emparts['p2consume'],emparts['p2consumecounter'],emparts['p2supply'],emparts['p2supplycounter']))
  print ('S: consume:{}VA {}kVAh supply:{}VA {}kVAh'.format(emparts['s2consume'],emparts['s2consumecounter'],emparts['s2supply'],emparts['s2supplycounter']))
  print ('Q: cap {}var {}kvarh ind {}var {}kvarh'.format(emparts['q2consume'],emparts['q2consumecounter'],emparts['q2supply'],emparts['q2supplycounter']))
  print ('U: {}V thd:{}% cos phi:{}°'.format(emparts['v2'],emparts['thd2'],emparts['cosphi2']))
  print ('----L3----')
  print ('P: consume:{}W {}kWh supply:{}W {}kWh'.format(emparts['p3consume'],emparts['p3consumecounter'],emparts['p3supply'],emparts['p3supplycounter']))
  print ('S: consume:{}VA {}kVAh supply:{}VA {}kVAh'.format(emparts['s3consume'],emparts['s3consumecounter'],emparts['s3supply'],emparts['s3supplycounter']))
  print ('Q: cap {}var {}kvarh ind {}var {}kvarh'.format(emparts['q3consume'],emparts['q3consumecounter'],emparts['q3supply'],emparts['q3supplycounter']))
  print ('U: {}V thd:{}% cos phi:{}°'.format(emparts['v3'],emparts['thd3'],emparts['cosphi3']))
