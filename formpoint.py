import numpy as np
from read_data import dates_list

class FormPoint():
    def __init__(self, init_df=None, init_dict=None):
        self.point_dict = {}
        if init_df is None and not init_dict is None:
            self.point_dict=init_dict
        else:
            for l in init_df['lk_name'].drop_duplicates().tolist():
                self.point_dict[l]=np.array([init_df.loc[init_df['lk_name']==l,d] for d in dates_list])

    def __getitem__(self, d):
        """
        :param d: date to form list
        """
        return [vec[dates_list.index(d)] for vec in self.point_dict.values()]

    def __add__(self,other):
        answ = {}
        if isinstance(other, FormPoint):
            for l, vec in self.point_dict.items():
                if l in other.point_dict:
                    if any(not np.isnan(v) for v in vec) and any(not np.isnan(v) for v in other.point_dict[l]):
                        answ[l]=vec+other.point_dict[l]
                    else:
                        answ[l]=np.empty(len(vec)).fill(np.nan)
                else:
                    answ[l]= np.empty(len(vec)).fill(np.nan)
            return FormPoint(init_dict=answ)
        elif isinstance(other,(int, float, np.ndarray, np.int32, np.int64, np.float64)):
            for l, vec in self.point_dict.items():
                    if any(not np.isnan(v) for v in vec):
                        answ[l]=vec+other
                    else:
                        answ[l]=np.empty(len(vec)).fill(np.nan)
            return FormPoint(init_dict=answ)

    def __sub__(self,other):
        if isinstance(other, FormPoint):
            for l in other.point_dict.keys():
                other.point_dict[l]*=(-1)
            return self+other
        elif isinstance(other,(int, float, np.ndarray, np.int32, np.int64, np.float64)):
            other*=(-1)
            return self+other

    def __mul__(self,other):
        answ = {}
        if isinstance(other, FormPoint):
            for l, vec in self.point_dict.items():
                if l in other.point_dict:
                    if any(not np.isnan(v) for v in vec) and any(not np.isnan(v) for v in other.point_dict[l]):
                        answ[l] = vec * other.point_dict[l]
                    else:
                        answ[l] = np.empty(len(vec)).fill(np.nan)
                else:
                    answ[l] = np.empty(len(vec)).fill(np.nan)
            return FormPoint(init_dict=answ)
        elif isinstance(other, (int, float, np.ndarray, np.int32, np.int64, np.float64)):
            for l, vec in self.point_dict.items():
                if any(not np.isnan(v) for v in vec):
                    answ[l] = vec * other
                else:
                    answ[l] = np.empty(len(vec)).fill(np.nan)
            return FormPoint(init_dict=answ)

    def __truediv__(self, other):
        if isinstance(other, FormPoint):
            for l in other.point_dict.keys():
                for i in range(len(other.point_dict[l])):
                    other.point_dict[l][i] = 1/other.point_dict[l][i] if not other.point_dict[l][i]==0 else None
            return self * other
        elif isinstance(other, (int, float, np.ndarray, np.int32, np.int64, np.float64)):
            if isinstance(other,np.ndarray):
                for i in range(len(other)):
                    other[i]=1/other[i] if not other[i]==0 else None
            else:
                other = 1/other if not other==0 else None
            return self * other

