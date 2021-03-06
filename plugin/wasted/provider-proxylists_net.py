from __future__ import unicode_literals, absolute_import, division, print_function
import json
import re
import logging
import os, sys, time


if __name__ == '__main__':
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    sys.path.append(sys.path[0]+"\\plugin")

from provider import *

class Proxy(ProxyWithWebdriver):

    def __init__(self):
        urls =  [ 'http://www.proxylists.net/',
            'http:/www.proxylists.net/af_0.html',
            'http:/www.proxylists.net/al_0.html',
            'http:/www.proxylists.net/ar_0.html',
            'http:/www.proxylists.net/am_0.html',
            'http:/www.proxylists.net/au_0.html',
            'http:/www.proxylists.net/at_0.html',
            'http:/www.proxylists.net/az_0.html',
            'http:/www.proxylists.net/bd_0.html',
            'http:/www.proxylists.net/by_0.html',
            'http:/www.proxylists.net/be_0.html',
            'http:/www.proxylists.net/bo_0.html',
            'http:/www.proxylists.net/ba_0.html',
            'http:/www.proxylists.net/bw_0.html',
            'http:/www.proxylists.net/br_0.html',
            'http:/www.proxylists.net/bg_0.html',
            'http:/www.proxylists.net/bf_0.html',
            'http:/www.proxylists.net/kh_0.html',
            'http:/www.proxylists.net/cm_0.html',
            'http:/www.proxylists.net/ca_0.html',
            'http:/www.proxylists.net/cl_0.html',
            'http:/www.proxylists.net/cn_0.html',
            'http:/www.proxylists.net/co_0.html',
            'http:/www.proxylists.net/cg_0.html',
            'http:/www.proxylists.net/cr_0.html',
            'http:/www.proxylists.net/cd_0.html',
            'http:/www.proxylists.net/hr_0.html',
            'http:/www.proxylists.net/cy_0.html',
            'http:/www.proxylists.net/cz_0.html',
            'http:/www.proxylists.net/dk_0.html',
            'http:/www.proxylists.net/ec_0.html',
            'http:/www.proxylists.net/eg_0.html',
            'http:/www.proxylists.net/sv_0.html',
            'http:/www.proxylists.net/eu_0.html',
            'http:/www.proxylists.net/fr_0.html',
            'http:/www.proxylists.net/ge_0.html',
            'http:/www.proxylists.net/de_0.html',
            'http:/www.proxylists.net/gh_0.html',
            'http:/www.proxylists.net/gb_0.html',
            'http:/www.proxylists.net/gr_0.html',
            'http:/www.proxylists.net/gt_0.html',
            'http:/www.proxylists.net/hn_0.html',
            'http:/www.proxylists.net/hk_0.html',
            'http:/www.proxylists.net/hu_0.html',
            'http:/www.proxylists.net/zz_0.html',
            'http:/www.proxylists.net/in_0.html',
            'http:/www.proxylists.net/id_0.html',
            'http:/www.proxylists.net/ir_0.html',
            'http:/www.proxylists.net/iq_0.html',
            'http:/www.proxylists.net/ie_0.html',
            'http:/www.proxylists.net/il_0.html',
            'http:/www.proxylists.net/it_0.html',
            'http:/www.proxylists.net/jm_0.html',
            'http:/www.proxylists.net/jp_0.html',
            'http:/www.proxylists.net/jo_0.html',
            'http:/www.proxylists.net/kz_0.html',
            'http:/www.proxylists.net/ke_0.html',
            'http:/www.proxylists.net/kr_0.html',
            'http:/www.proxylists.net/kg_0.html',
            'http:/www.proxylists.net/la_0.html',
            'http:/www.proxylists.net/lv_0.html',
            'http:/www.proxylists.net/lb_0.html',
            'http:/www.proxylists.net/ls_0.html',
            'http:/www.proxylists.net/ly_0.html',
            'http:/www.proxylists.net/lt_0.html',
            'http:/www.proxylists.net/mk_0.html',
            'http:/www.proxylists.net/mw_0.html',
            'http:/www.proxylists.net/my_0.html',
            'http:/www.proxylists.net/ml_0.html',
            'http:/www.proxylists.net/mt_0.html',
            'http:/www.proxylists.net/mu_0.html',
            'http:/www.proxylists.net/mx_0.html',
            'http:/www.proxylists.net/md_0.html',
            'http:/www.proxylists.net/mn_0.html',
            'http:/www.proxylists.net/mz_0.html',
            'http:/www.proxylists.net/mm_0.html',
            'http:/www.proxylists.net/np_0.html',
            'http:/www.proxylists.net/nl_0.html',
            'http:/www.proxylists.net/nz_0.html',
            'http:/www.proxylists.net/ni_0.html',
            'http:/www.proxylists.net/ng_0.html',
            'http:/www.proxylists.net/no_0.html',
            'http:/www.proxylists.net/pk_0.html',
            'http:/www.proxylists.net/ps_0.html',
            'http:/www.proxylists.net/pa_0.html',
            'http:/www.proxylists.net/py_0.html',
            'http:/www.proxylists.net/pe_0.html',
            'http:/www.proxylists.net/ph_0.html',
            'http:/www.proxylists.net/pl_0.html',
            'http:/www.proxylists.net/pt_0.html',
            'http:/www.proxylists.net/pr_0.html',
            'http:/www.proxylists.net/ro_0.html',
            'http:/www.proxylists.net/ru_0.html',
            'http:/www.proxylists.net/sl_0.html',
            'http:/www.proxylists.net/sg_0.html',
            'http:/www.proxylists.net/sk_0.html',
            'http:/www.proxylists.net/si_0.html',
            'http:/www.proxylists.net/so_0.html',
            'http:/www.proxylists.net/za_0.html',
            'http:/www.proxylists.net/es_0.html',
            'http:/www.proxylists.net/se_0.html',
            'http:/www.proxylists.net/sy_0.html',
            'http:/www.proxylists.net/tw_0.html',
            'http:/www.proxylists.net/tz_0.html',
            'http:/www.proxylists.net/th_0.html',
            'http:/www.proxylists.net/tt_0.html',
            'http:/www.proxylists.net/tr_0.html',
            'http:/www.proxylists.net/ug_0.html',
            'http:/www.proxylists.net/ua_0.html',
            'http:/www.proxylists.net/ae_0.html',
            'http:/www.proxylists.net/us_0.html',
            'http:/www.proxylists.net/uy_0.html',
            'http:/www.proxylists.net/ve_0.html',
            'http:/www.proxylists.net/vn_0.html',
            'http:/www.proxylists.net/zm_0.html',
        ]
        super().__init__(urls, time_load_page=30, multi_page='Y' )
            
if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
