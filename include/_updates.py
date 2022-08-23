import numpy as np
import pandas as pd
from include._sisso import make_hull, regr_line

def update_symbols ( self ):
 
    for cl in range(self.n_classes):

        name_trace = 'Class ' + str(self.classes[cl])
        self.symbols[name_trace] = [self.class_symbol[name_trace]] * len(self.df_classes_on_map[name_trace])
        formula_l = self.widg_compound_text_l.value 
        formula_r = self.widg_compound_text_r.value 
        for i in range(2):
            try:
                point = np.where(self.df_classes_on_map[name_trace].index.to_numpy() == formula_l)[0][i]
                self.symbols[name_trace][point] = 'x'
            except:
                pass
            try:
                point = np.where(self.df_classes_on_map[name_trace].index.to_numpy() == formula_r)[0][i]
                self.symbols[name_trace][point] = 'cross'
            except:
                pass

        if (formula_l == formula_r and formula_l ):
            try:
                point = np.where(self.df_classes_on_map[name_trace].index.to_numpy() == formula_l)[0][1]
                self.symbols[name_trace][point] = 'x'
                point = np.where(self.df_classes_on_map[name_trace].index.to_numpy() == formula_l)[0][2]
                self.symbols[name_trace][point] = 'cross'
            except:
                pass

def update_markers_size( self ):
    # Defines the size of the markers based on the input feature.
    # In case of default feature all markers have the same size.
    # Points marked with x/cross are set with a specific size
    feature = self.widg_featmarker.value

    if feature == 'Default size':

        for cl in range(self.n_classes):

            name_trace = 'Class ' + str(self.classes[cl])

            sizes = [self.marker_size] * len(self.df_classes_on_map[name_trace])
            symbols = self.symbols[name_trace]

            indices_x = [i for i, symbol in enumerate(symbols) if symbol == "x"]
            indices_cross = [i for i, symbol in enumerate(symbols) if symbol == "cross"]

            if indices_x:
                sizes[indices_x[0]] = self.cross_size

            if (len(indices_x) == 2):
                sizes[indices_x[0]] = 0
                sizes[indices_x[1]] = self.cross_size
            
            if indices_cross:
                sizes[indices_cross[0]] = self.cross_size

            if (len(indices_cross) == 2):  
                sizes[indices_cross[0]] = 0
                sizes[indices_cross[1]] = self.cross_size

            self.sizes[name_trace] = sizes
    else:
        min_value = self.min_value_markerfeat
        max_value = self.max_value_markerfeat
        min_feat = min([min(self.df_classes_on_map[name_trace][feature].to_numpy()) for name_trace in self.df_classes_on_map])
        max_feat = max([max(self.df_classes_on_map[name_trace][feature].to_numpy()) for name_trace in self.df_classes_on_map])

        coeff = (max_value-min_value)/(max_feat-min_feat)

        for cl in range(self.n_classes):
            name_trace = 'Class ' + str(self.classes[cl])
            sizes = min_value + coeff * (self.df_classes_on_map[name_trace][feature].to_numpy()-min_feat)
            self.sizes[name_trace] = sizes


def update_layout_figure( self ):
    # All batch_update related changes are handled by this function

    x_min = []
    x_max = []
    y_min = []
    y_max = []

    for cl in np.arange(self.n_classes):
        name_trace = 'Class ' + str(self.classes[cl])
        x_min.append(min(self.df_classes_on_map[name_trace][self.feat_x]))
        x_max.append(max(self.df_classes_on_map[name_trace][self.feat_x]))
        y_min.append(min(self.df_classes_on_map[name_trace][self.feat_y]))
        y_max.append(max(self.df_classes_on_map[name_trace][self.feat_y]))
    x_min = min(x_min)
    y_min = min(y_min)
    x_max = max(x_max)
    y_max = max(y_max)
    x_delta = 0.05 * abs(x_max - x_min)
    y_delta = 0.05 * abs(y_max - y_min)
    xaxis_range =[x_min - x_delta, x_max + x_delta]
    yaxis_range=[y_min - y_delta, y_max + y_delta]

    update_symbols(self)
    update_markers_size(self)

    with self.fig.batch_update():
        self.fig.update_layout(
            showlegend=True,
            plot_bgcolor=self.bg_color,
            font=dict(
                size=int(self.font_size),
                family=self.widg_fontfamily.value,
                color=self.widg_fontcolor.value
            ),
            xaxis_title=self.widg_featx.value,
            yaxis_title=self.widg_featy.value,
            xaxis_range = xaxis_range,
            yaxis_range = yaxis_range,
        )
        for  cl in np.arange(self.n_classes):
            # All elements on the map and their properties are reinitialized at each change
            name_trace = 'Class ' + str(self.classes[cl])
            self.trace['Class ' + str(self.classes[cl])]['x'] = self.df_classes_on_map[name_trace][self.feat_x]
            self.trace['Class ' + str(self.classes[cl])]['y'] = self.df_classes_on_map[name_trace][self.feat_y]
            self.trace['Class ' + str(self.classes[cl])].marker.size = self.sizes[name_trace]
            self.trace['Class ' + str(self.classes[cl])].marker.symbol = self.symbols[name_trace]

            self.fig.update_traces(
                selector={'name': 'Class ' + str(self.classes[cl]) },
                text=self.hover_text[cl],
                customdata=self.hover_custom[cl],
                hovertemplate=self.hover_template[cl],
                marker_color=self.colors['Class ' + str(self.classes[cl])],
            )
        if ( self.convex_hull == True ) :

            if ( self.feat_x == self.feat_y ):
                for cl in np.arange(self.n_classes):
                    self.trace['Hull '+str(self.classes[cl])].line = dict ( width=0 )
                    self.fig.update_traces(
                        selector={'name': 'Hull '+str(self.classes[cl])},
                    )            
            else:
                hullx, hully = make_hull(self, self.feat_x, self.feat_y)
                for cl in np.arange(self.n_classes):
                    self.trace['Hull '+str(self.classes[cl])]['x'] = hullx[cl]
                    self.trace['Hull '+str(self.classes[cl])]['y'] = hully[cl]
                    self.trace['Hull '+str(self.classes[cl])].line = dict (color=self.widg_color_hull.value, width=self.widg_width_hull.value, dash=self.widg_style_hull.value )
                    self.fig.update_traces(
                        selector={'name': 'Hull '+str(self.classes[cl])},
                    )
        if ( self.regr_line_coefs ) :

            line_x, line_y = regr_line(self, self.feat_x, self.feat_y)
            self.trace['Regression line'].line = dict (color=self.widg_color_line.value, width=self.widg_width_line.value, dash=self.widg_style_line.value )
            self.trace['Regression line']['x'] = line_x
            self.trace['Regression line']['y'] = line_y



def update_df_on_map(self):

    for cl in range(self.n_classes):

        name_trace = 'Class ' + str(self.classes[cl])
        n_points = int(self.frac * self.df_classes[cl].shape[0])
        if n_points < 1:
            n_points = 1
        self.n_points[name_trace]= n_points

        self.df_classes_on_map[name_trace] = self.df_classes[cl].loc[self.index_classes_shuffled[cl]].head(self.n_points[name_trace])

        if self.widg_compound_text_l.value in self.df_classes[cl].index:
            self.df_classes_on_map[name_trace] = pd.concat([self.df_classes_on_map[name_trace], self.df.loc[[self.widg_compound_text_l.value]] ])

            # self.df_classes_on_map[name_trace] = pd.concat([ self.df.loc[[self.widg_compound_text_l.value]], self.df_classes_on_map[name_trace] ])

        if self.widg_compound_text_r.value in self.df_classes[cl].index:
            self.df_classes_on_map[name_trace] = pd.concat([self.df_classes_on_map[name_trace], self.df.loc[[self.widg_compound_text_r.value]] ])

            # self.df_classes_on_map[name_trace] = self.df_classes_on_map[name_trace].append(self.df.loc[self.widg_compound_text_r.value])
            

def update_hover_variables(self):
    self.hover_text = []
    self.hover_custom = []
    self.hover_template = []

    for cl in range(self.n_classes):
        name_trace = 'Class ' + str(self.classes[cl])
        self.hover_text.append(self.df_classes_on_map[name_trace].index)
        hover_template = r"<b>%{text}</b><br><br>"
        if self.hover_features:
            hover_custom = np.dstack([self.df_classes_on_map[name_trace][str(self.hover_features[0])].to_numpy()])
            hover_template += str(self.hover_features[0]) + ": %{customdata[0]}<br>"
            for i in range(1, len(self.hover_features), 1):
                hover_custom = np.dstack(
                    [hover_custom, self.df_classes_on_map[name_trace][str(self.hover_features[i])].to_numpy()])
                hover_template += str(self.hover_features[i]) + ": %{customdata[" + str(i) + "]}<br>"
            self.hover_custom.append(hover_custom[0])
            self.hover_template.append(hover_template)
        else:
            self.hover_custom.append([''])
            self.hover_template.append([''])


