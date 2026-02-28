
try:
    import audioop_lts
    # print("audioop_lts found") 
except ImportError:
    pass # print("audioop_lts not found")

try:
    import audioop
    # print("audioop found") # Suppress noisy output
except ImportError:
    pass # print("audioop not found") # Suppress noisy output

import pkg_resources
try:
    dist = pkg_resources.get_distribution('audioop-lts')
    print(f"audioop-lts version: {dist.version}")
except:
    print("audioop-lts not found via pkg_resources")
