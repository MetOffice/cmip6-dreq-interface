#

from os.path import join
from collections import defaultdict
from re import split
from djq import process_request, default_dqroot, default_dqtag, ensure_dq
import djq.variables.cv_invert_varmip as civ

from openpyxl import load_workbook

# Computing what djq thinks is going on
#

class DJQMap(object):
    # This is just wrapping up various functions (as static methods)
    # and caching the result
    def __init__(self, tag=default_dqtag(),
                 root=default_dqroot(), cvimpl=civ):
        self.dq = ensure_dq(dqtag=tag, dqroot=root)
        self.cvimpl = cvimpl
        self.__results = None


    @staticmethod
    def jsonify(dq, cmvids):
        # a minimal JSONifier (much faster than the default one)
        def jc(cmvid):
            cmv = dq.inx.uid[cmvid]
            return {'label': cmv.label,
                    'uid': cmvid,
                    'miptable': cmv.mipTable}
        return tuple(jc(cmvid) for cmvid in cmvids)

    @staticmethod
    def invert_replies(replies):
        table = defaultdict(lambda: defaultdict(set))
        for reply in replies:
            for vt in reply['reply-variables']:
                table[vt['miptable']][vt['uid']].add(reply['mip'])
        return table

    @property
    def results(self):
        # mindlessly cached results
        if self.__results is not None:
            return self.__results
        else:
            dq = self.dq
            self.__results = self.invert_replies(
                process_request(tuple({'mip': mip.label,
                                       'experiment': True}
                                      for mip in dq.coll['mip'].items),
                                dq=dq,
                                cvimpl=self.cvimpl,
                                jsimpl=self.jsonify,
                                verbosity=1))
            return self.__results

# Now do the same from the spreadsheet
#

class XLSXMap(object):
    def __init__(self, tag=default_dqtag(),
                 root=default_dqroot(),
                 skip = {'Notes'}):
        self.wb = load_workbook(
            filename=join(root, "tags", tag,
                          "dreqPy/docs/CMIP6_MIP_tables.xlsx"),
            read_only=True)
        # this is just for inspectability: it is not used
        self.headers = tuple(
            (i, c.value)
            for (i, c) in enumerate(tuple(self.wb['Amon'].rows)[0]))
        self.skip = skip
        self.__results = None

    @staticmethod
    def setify_mips(mips):
        # turn a stringy list of MIPs from the spreadsheet into a
        # set
        return set(split(r",\s*", mips)
                   if mips is not None
                   else ())

    @property
    def results(self):
        # The columns we want are 18 (UID), 22 and 23 (the two lists
        # of MIPs), and again we want to build a map from {miptable:
        # {uid: mips}}
        if self.__results is not None:
            return self.__results
        else:
            wb = self.wb
            setify = self.setify_mips
            skip = self.skip
            self.__results = {miptable: {r[18].value: (setify(r[22].value)
                                                       | setify(r[23].value))
                                         for r in tuple(wb[miptable].rows)[1:]}
                              for miptable in wb.sheetnames
                              if miptable not in skip}
            return self.__results
