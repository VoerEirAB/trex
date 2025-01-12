from trex_stl_lib.api import *

# Example of STLVmFlowVarRepetableRandom instruction. 
# in this case it generate repetable random numbers with limit/seed

class STLS1(object):

    def __init__ (self):
        self.fsize  =64;

    def create_stream (self, direction, cache_size):
        # Create base packet and pad it to size
        size = self.fsize - 4; # HW will add 4 bytes ethernet FCS
        src_ip = '16.0.0.1'
        dst_ip = '48.0.0.1'
        if direction:
            src_ip, dst_ip = dst_ip, src_ip

        base_pkt = Ether()/IP(src=src_ip,dst=dst_ip)/UDP(dport=12,sport=1025)

        pad = max(0, size - len(base_pkt)) * 'x'

        src_fv = STLVmFlowVarRepetableRandom(
            name="ip_src",
            min_value="10.0.0.0",
            max_value="10.0.0.10",
            size=4,
            limit=10),
        dst_fv = STLVmFlowVarRepetableRandom(
            name="ip_dst",
            min_value="10.0.0.0",
            max_value="10.0.0.10",
            size=4,
            limit=10)

                             
        vm = STLScVmRaw( [   src_fv,
                             STLVmWrFlowVar (fv_name="ip_src", pkt_offset= "IP.src" ), # write ip to packet IP.src
                             dst_fv,
                             STLVmWrFlowVar (fv_name="ip_dst", pkt_offset= "IP.dst" ), # write ip to packet IP.dst


                             STLVmFixIpv4(offset = "IP")                                # fix checksum
                                  ]
                              ,split_by_field = "ip_src"  # split to cores base on the tuple generator 
                              ,cache_size = cache_size # the cache size
                              );

        pkt = STLPktBuilder(pkt = base_pkt/pad,
                            vm = vm)
        stream = STLStream(packet = pkt,
                         mode = STLTXCont())
        #print(stream.to_code())
        return stream


    def get_streams (self, direction = 0, cache_size = 255, **kwargs):
        # create 1 stream 
        return [ self.create_stream(direction, cache_size) ]


# dynamic load - used for trex console or simulator
def register():
    return STLS1()



