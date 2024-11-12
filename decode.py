# 0x664cba37000000000000fa42184cbd2ea76d0000000000000168d40445dc31b7

def hex_to_int(hex_str):
    return int(hex_str, 16)

def decode_rs(num: int):
    bit_length = num.bit_length() + 1
    uint32_bits = 32
    u112_bits = 112

    ts = num >> (bit_length - uint32_bits)
    shift_for_second_part = bit_length - uint32_bits - u112_bits
    rs1 = (num >> shift_for_second_part) & ((1 << u112_bits) - 1)
    rs0 = num & ((1 << u112_bits) - 1)

    return ts, rs0, rs1


if __name__ == '__main__':
    input = "0x664c9e83000000000003043c5f0a5c4e303c00000000000147831c24211d2fa9"
    num_converted = hex_to_int(input)
    ts, rs0, rs1 = decode_rs(num_converted)
    print(f"ts: {ts}, rs0: {rs0}, rs1: {rs1}")
    print(f"ts: {ts}, rs0: {rs0/1e9}, rs1: {rs1/1e18}")
