import networkx as nx
import pickle
import codecs
import random
import os


class explan:
    def __init__(self):
        self.relation_list = []
        self.kg = ''
        self.watch_his = ''
        self.path = dict()
        self.long_path = dict()

    def loadpk(self):
        if not self.kg:
            if os.path.exists("kg.pkl"):
                with open("kg.pkl", "rb") as f:
                    self.kg = pickle.load(f)
                    G = self.kg
            else:
                G = nx.read_edgelist('dbo_allrelations.edgelist', data=True, delimiter='\t')
                with open("kg.pkl", "wb") as f:
                    pickle.dump(G, f)
        else:
            G = self.kg
        return G

    def load_watch(self):
        if not self.watch_his:
            if os.path.exists("watched_dict.pickle"):
                with open("watched_dict.pickle", "rb") as f:
                    self.watch_his = pickle.load(f)
            else:
                print("have not watched_dict.pickle")
        return self.watch_his

    def get_explanation(self, line):
        G = self.loadpk()
        watch_dict = self.load_watch()
        rec_dict = dict()
        result_dict = dict()
        uid, rec_list = line.split("\t")
        watch_list = watch_dict[int(uid)]
        for rec in rec_list.split(",")[10:20]:
            ur = uid + '_' + rec
            if ur not in rec_dict:
                rec_dict[ur] = []
                self.path[ur] = []
            for watch in watch_list:
                try:
                    p = nx.shortest_path(G, source=str(rec), target=str(watch))
                    # self.path[ur].append(p)
                    result = []
                    for index, node in enumerate(p):
                        result.append(node)
                        if index < len(p) - 1:
                            result.append(G[node][p[index + 1]]['name'])
                    #             print(result)
                    #             relation = ['导演','编剧','主演','类型','发行国家','发行年份','语言']
                    # self.long_path[ur] = result
                    if len(result) < 10:
                        rec_dict[ur].append([result, p])
                except:
                    continue
        for k, v in rec_dict.items():
            try:
                temp = random.choice(v)
                reason = temp[0]
                #     print(reason)
                if len(reason) == 5:
                    result_dict[k] = [self.select_mode(reason[1], reason[2]), temp]
                elif len(reason) == 9:
                    self.relation_list.append([reason[1], reason[5]])
                    relation = ['导演', '编剧', '主演', '发行国家', '语言']
                    for i, re in enumerate(reason):
                        if re in relation:
                            result_dict[k] = [self.select_mode(reason[i], reason[i + 1]), temp]
                            break
            except Exception:
                continue
        return result_dict

    def mov_type(self, reason):
        exp_list = ["用户非常喜欢类型为" + reason + '的影片，所以给他推荐了同类影片。',
                    "根据你选看电影类型，给你推荐" + reason + "类型的影片。"]
        result = random.choice(exp_list)
        return result

    def mov_language(self, reason):
        exp_list = ["看来" + reason + "片是你的最爱，推荐一部非常棒的电影给你哟。",
                    "原来你最近在看" + reason + "的影片，给你推荐一部很棒的该语言影片。"]
        result = random.choice(exp_list)
        return result

    def mov_area(self, reason):
        exp_list = ["不要问我为什么，" + reason + "的电影是你的最爱！",
                    "该片太棒了，根据你的喜好，给你推荐" + reason + "地区影片。"]
        result = random.choice(exp_list)
        return result

    def mov_publish_time(self, reason):
        exp_list = ["时间是你选择电影的首要因素，给你推荐" + reason + "的电影，希望你喜欢。",
                    "给你推荐一部" + reason + "的影片，不要惊讶哟，因为你看了好多这个时间段的电影。"]
        result = random.choice(exp_list)
        return result

    def mov_director(self, reason):
        exp_list = [reason + "执导的电影确实值得一看，这里给你推荐一部。",
                    "导演" + reason + "的这部影片你是不是错过了？我知道你喜欢" + reason+"。"]
        result = random.choice(exp_list)
        return result

    def mov_screen_writer(self, reason):
        exp_list = [reason + "编剧太牛了，说实话，我也喜欢" + reason + "的作品。",
                    "编剧" + reason + "的这部影片不能错过，你不会失望的。"]
        result = random.choice(exp_list)
        return result

    def mov_actor(self, reason):
        exp_list = [reason + "主演电影棒棒的",
                    reason + "演的这部影片太棒了，值得一看哟"]
        result = random.choice(exp_list)
        return result

    def select_mode(self, rel, reason):
        if rel == '类型':
            result = self.mov_type(reason)
            return result
        elif rel == '主演':
            result = self.mov_actor(reason)
            return result
        elif rel == '编剧':
            result = self.mov_screen_writer(reason)
            return result
        elif rel == '语言':
            result = self.mov_language(reason)
            return result
        elif rel == '导演':
            result = self.mov_director(reason)
            return result
        elif rel == '发行国家':
            result = self.mov_area(reason)
            return result
        else:
            result = self.mov_publish_time(reason)
            return result


if __name__ == "__main__":
    exp = explan()
    with codecs.open("ripple_result.txt", "r", "utf-8") as f:
        for line in f.readlines():
            uid_mid_rec = exp.get_explanation(line.strip())
        print(set(exp.relation_list))