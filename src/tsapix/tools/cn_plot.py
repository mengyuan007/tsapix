import matplotlib.pyplot as plt
import tsapi
import talib
import numpy as np
import streamlit as st

from matplotlib import font_manager

fontP = font_manager.FontProperties()
fontP.set_family('SimHei')
fontP.set_size(14)


def obs_names_at_specific_mth(_names=[], _ym="xxxx-xx",
                              xobj=None, 
                              code_name_mapdict=None,
                              xpd_ma20=None,
                              xpd_ma5=None,
                              b_low=None,
                              b_up=None,
                              xpd=None,
                              obs_step=20,
                              additional_info=[],
                              savepath=None,
                              show=True
                              ):
# _names = ['603099',]
# _ym = '2024-01'
    histpx_d_qfq_axes = xobj['axes']
    pxpddict = xobj

    _dates = [x for x in histpx_d_qfq_axes['1str'] if _ym in x]
    _start_date_id = histpx_d_qfq_axes['1str'].index(_dates[0])
    _end_date_id = histpx_d_qfq_axes['1str'].index(_dates[-1])

    _plot_range = slice(_start_date_id-obs_step, _end_date_id+obs_step)
    _fig_size = (16, 5)
    _ber_length = 0.3


    xxid = 0
    for _plot_ticker in _names[:]:
        try:
            print(_plot_ticker, code_name_mapdict[_plot_ticker]['name'], end=";")
        except:
            pass
        if len(additional_info)>0:
            for adxsuit in additional_info:
                if type(adxsuit) in [list, tuple]:
                    if len(adxsuit)==2:
                        adx, _prefix = adxsuit
                        _suffix = ''
                    else:
                        adx, _prefix, _suffix = adxsuit
                else:
                    adx = adxsuit
                    _prefix, _suffix = '', ''
                try:
                    print(_prefix, adx[_plot_ticker], _suffix, end=";")
                except:
                    pass
        
        # _loc_id = histpx_d_qfq_axes[2].index(_plot_ticker)

        fig, axs = plt.subplots(figsize=_fig_size)
        xs = [x.strftime("%Y-%m-%d") for x in histpx_d_qfq_axes[1][_plot_range]]
        xvs = range(len(xs))
        xticks = range(-len(xs), 0)
        axs.set_xticklabels(xticks)
        
        _plt_open = pxpddict['Open'][_plot_ticker].iloc[_plot_range]
        _plt_high = pxpddict['High'][_plot_ticker].iloc[_plot_range]
        _plt_low = pxpddict['Low'][_plot_ticker].iloc[_plot_range]
        _plt_close = pxpddict['Close'][_plot_ticker].iloc[_plot_range]
        _px_colors = np.where(_plt_close>_plt_open, 'firebrick', 'darkslateblue')
        
        _tr = pxpddict['TurnoverRate'][_plot_ticker].iloc[_plot_range]
        
        try:
            axs.vlines(
                xs, 
                list(_plt_low.values), 
                list(_plt_high.values), 
                color=_px_colors,
                label=code_name_mapdict[_plot_ticker]['name'],
            )
        except:
            axs.vlines(
                    xs, 
                    list(_plt_low.values), 
                    list(_plt_high.values), 
                    color=_px_colors,
                )
        # plt.legend(loc=0, prop=fontP)
        axs.hlines(
            _plt_open, 
            np.array(xvs) - _ber_length, 
            xvs,
            color=_px_colors,
        )
        axs.hlines(
            _plt_close, 
            xvs, 
            np.array(xvs) + _ber_length,
            color=_px_colors,
        )
        
        try:
            axs.plot(xs, xpd_ma20[_plot_ticker].iloc[_plot_range].values, color='orange')
        #     axs.plot(xs, xpd_ma10[_plot_ticker].iloc[_plot_range].values, color='grey')
            axs.plot(xs, xpd_ma5[_plot_ticker].iloc[_plot_range].values, color='grey')
            
            axs.plot(xs, b_up[_plot_ticker].iloc[_plot_range].values, color='blue', alpha=0.5)
            axs.plot(xs, b_low[_plot_ticker].iloc[_plot_range].values, color='purple', alpha=0.5)
        except:
            pass

        axs_0 = axs.twinx()
        axs_0.vlines(obs_step, 0, 1, linestyles='--', colors='black')
        axs_0.vlines(len(xs) - obs_step, 0, 1, linestyles='--', colors='black')

        if savepath is not None:
            try:
                fig.savefig(f"{savepath}/{xxid}_{_plot_ticker}_{code_name_mapdict[_plot_ticker]['name']}.png", bbox_inches='tight')
            except:
                fig.savefig(f"{savepath}/{xxid}_{_plot_ticker}.png", bbox_inches='tight')
        
        fig, axs = plt.subplots(figsize=(16, 3))
        l1pd, l2pd, lhistpd = talib.MACD(xpd[_plot_ticker], fastperiod=12, slowperiod=26, signalperiod=9)
        axs.plot(xvs, l1pd.iloc[_plot_range], color='orange')
        axs.plot(xvs, l2pd.iloc[_plot_range], color='blue')
        axs.bar(xvs, lhistpd.iloc[_plot_range], color='blue')

        if savepath is not None:
            fig.savefig(f"{savepath}/{xxid}_{_plot_ticker}_macd.png", bbox_inches='tight')
        
        if show:
            plt.show()

        xxid+=1

def obs_names_at_specific_mth_v2(_names=[], _ym="xxxx-xx",
                              xobj=None, 
                              code_name_mapdict=None,
                              xpd_ma20=None,
                              xpd_ma5=None,
                              b_low=None,
                              b_up=None,
                              xpd=None,
                              obs_step=20,
                              additional_info=[],
                              savepath=None,
                              show=True,
                              alertedindo=None
                              ):
# _names = ['603099',]
# _ym = '2024-01'
    histpx_d_qfq_axes = xobj['axes']
    pxpddict = xobj

    _dates = [x for x in histpx_d_qfq_axes['1str'] if _ym in x]
    _start_date_id = histpx_d_qfq_axes['1str'].index(_dates[0])
    _end_date_id = histpx_d_qfq_axes['1str'].index(_dates[-1])

    _plot_range = slice(_start_date_id-obs_step, _end_date_id+obs_step)
    _fig_size = (16, 5+2+2)
    _ber_length = 0.3


    xxid = 0
    for _plot_ticker in _names[:]:
        try:
            print(_plot_ticker, code_name_mapdict[_plot_ticker]['name'], end=";")
        except:
            pass
        if len(additional_info)>0:
            for adxsuit in additional_info:
                if type(adxsuit) in [list, tuple]:
                    if len(adxsuit)==2:
                        adx, _prefix = adxsuit
                        _suffix = ''
                    else:
                        adx, _prefix, _suffix = adxsuit
                else:
                    adx = adxsuit
                    _prefix, _suffix = '', ''
                try:
                    print(_prefix, adx[_plot_ticker], _suffix, end=";")
                except:
                    pass
        
        # _loc_id = histpx_d_qfq_axes[2].index(_plot_ticker)

        fig, axs = plt.subplots(nrows=3, ncols=1, height_ratios=[5, 2, 2], figsize=_fig_size, sharex=True, gridspec_kw=dict(hspace=0))
        # axs[0].plot(range(10), range(10))

        # fig, axs = plt.subplots(figsize=_fig_size)
        xs = [x.strftime("%Y-%m-%d") for x in histpx_d_qfq_axes[1][_plot_range]]
        xvs = range(len(xs))
        xticks = range(-len(xs), 0)
        axs[2].set_xticklabels(xticks)
        
        _plt_open = pxpddict['Open'][_plot_ticker].iloc[_plot_range]
        _plt_high = pxpddict['High'][_plot_ticker].iloc[_plot_range]
        _plt_low = pxpddict['Low'][_plot_ticker].iloc[_plot_range]
        _plt_close = pxpddict['Close'][_plot_ticker].iloc[_plot_range]
        _px_colors = np.where(_plt_close>_plt_open, 'firebrick', 'darkslateblue')
        
        _tr = pxpddict['TurnoverRate'][_plot_ticker].iloc[_plot_range]
        
        try:
            axs[0].vlines(
                xs, 
                list(_plt_low.values), 
                list(_plt_high.values), 
                color=_px_colors,
                label=code_name_mapdict[_plot_ticker]['name'],
            )
        except:
            axs[0].vlines(
                    xs, 
                    list(_plt_low.values), 
                    list(_plt_high.values), 
                    color=_px_colors,
                )
        # plt.legend(loc=0, prop=fontP)
        axs[0].hlines(
            _plt_open, 
            np.array(xvs) - _ber_length, 
            xvs,
            color=_px_colors,
        )
        axs[0].hlines(
            _plt_close, 
            xvs, 
            np.array(xvs) + _ber_length,
            color=_px_colors,
        )
        
        try:
            axs[0].plot(xs, xpd_ma20[_plot_ticker].iloc[_plot_range].values, color='orange')
        #     axs.plot(xs, xpd_ma10[_plot_ticker].iloc[_plot_range].values, color='grey')
            axs[0].plot(xs, xpd_ma5[_plot_ticker].iloc[_plot_range].values, color='grey')
            
            axs[0].plot(xs, b_up[_plot_ticker].iloc[_plot_range].values, color='blue', alpha=0.5)
            axs[0].plot(xs, b_low[_plot_ticker].iloc[_plot_range].values, color='purple', alpha=0.5)
        except:
            pass

        _plt_ema12 = pxpddict['Close'][_plot_ticker].ewm(span=12, adjust=False).mean()
        _plt_ema26 = pxpddict['Close'][_plot_ticker].ewm(span=26, adjust=False).mean()
        _plt_ema60 = pxpddict['Close'][_plot_ticker].ewm(span=60, adjust=False).mean()
        _plt_ema130 = pxpddict['Close'][_plot_ticker].ewm(span=130, adjust=False).mean()
        _plt_ema260 = pxpddict['Close'][_plot_ticker].ewm(span=260, adjust=False).mean()
        
        axs[0].plot(xvs, _plt_ema12.iloc[_plot_range], color='red', alpha=0.2)
        axs[0].plot(xvs, _plt_ema26.iloc[_plot_range], color='blue', alpha=0.2)
        axs[0].plot(xvs, _plt_ema60.iloc[_plot_range], color='orange', alpha=0.2)
        axs[0].plot(xvs, _plt_ema130.iloc[_plot_range], color='green', alpha=0.2)
        axs[0].plot(xvs, _plt_ema260.iloc[_plot_range], color='purple', alpha=0.2)

        if alertedindo is not None:
            _xs = [x for x in xs if int(x.replace("-", "")) in alertedindo.index]
            aids = [i for i in range(len(_xs)) if alertedindo[_plot_ticker].loc[int(_xs[i].replace("-", ""))]]

            axs[0].scatter([xs[i] for i in aids], [pxpddict['Close'][_plot_ticker].iloc[_plot_range].iloc[i] for i in aids], c='red', alpha=0.5, s=100)

        axs_0 = axs[0].twinx()
        axs_0.vlines(obs_step, 0, 1, linestyles='--', colors='black')
        axs_0.vlines(len(xs) - obs_step, 0, 1, linestyles='--', colors='black')

        _plt_volume = pxpddict['TurnoverRate'][_plot_ticker].iloc[_plot_range]
        _plt_pctchg = pxpddict['Close'][_plot_ticker].pct_change().iloc[_plot_range]
        volcolors = np.where(_plt_pctchg>0, 'red', 'green')
        axs[1].bar(xvs, _plt_volume, color=volcolors)


        # fig, axs = plt.subplots(figsize=(16, 3))
        l1pd, l2pd, lhistpd = talib.MACD(xpd[_plot_ticker], fastperiod=12, slowperiod=26, signalperiod=9)
        axs[2].plot(xvs, l1pd.iloc[_plot_range], color='orange')
        axs[2].plot(xvs, l2pd.iloc[_plot_range], color='blue')
        axs[2].bar(xvs, lhistpd.iloc[_plot_range], color='blue')

        import pandas as pd
        pd.DataFrame().ewm(span=12, adjust=False)

        plt.show(fig)

        xxid+=1


def obs_names_at_specific_mth_streamlit(_names=[], _ym="xxxx-xx",
                              xobj=None, 
                              code_name_mapdict=None,
                              xpd_ma20=None,
                              xpd_ma5=None,
                              b_low=None,
                              b_up=None,
                              xpd=None,
                              obs_step=20,
                              additional_info=[],
                              savepath=None,
                              show=True,
                              alertedindo=None
                              ):
# _names = ['603099',]
# _ym = '2024-01'
    histpx_d_qfq_axes = xobj['axes']
    pxpddict = xobj

    _dates = [x for x in histpx_d_qfq_axes['1str'] if _ym in x]
    _start_date_id = histpx_d_qfq_axes['1str'].index(_dates[0])
    _end_date_id = histpx_d_qfq_axes['1str'].index(_dates[-1])

    _plot_range = slice(_start_date_id-obs_step, _end_date_id+obs_step)
    _fig_size = (16, 5)
    _ber_length = 0.3


    xxid = 0
    for _plot_ticker in _names[:]:
        try:
            st.write(_plot_ticker, code_name_mapdict[_plot_ticker]['name'], end=";")
        except:
            pass
        if len(additional_info)>0:
            for adxsuit in additional_info:
                if type(adxsuit) in [list, tuple]:
                    if len(adxsuit)==2:
                        adx, _prefix = adxsuit
                        _suffix = ''
                    else:
                        adx, _prefix, _suffix = adxsuit
                else:
                    adx = adxsuit
                    _prefix, _suffix = '', ''
                try:
                    st.write(_prefix, adx[_plot_ticker], _suffix, end=";")
                except:
                    pass
        
        # _loc_id = histpx_d_qfq_axes[2].index(_plot_ticker)

        fig, axs = plt.subplots(figsize=_fig_size)
        xs = [x.strftime("%Y-%m-%d") for x in histpx_d_qfq_axes[1][_plot_range]]
        xvs = range(len(xs))
        xticks = range(-len(xs), 0)
        axs.set_xticklabels(xticks)
        
        _plt_open = pxpddict['Open'][_plot_ticker].iloc[_plot_range]
        _plt_high = pxpddict['High'][_plot_ticker].iloc[_plot_range]
        _plt_low = pxpddict['Low'][_plot_ticker].iloc[_plot_range]
        _plt_close = pxpddict['Close'][_plot_ticker].iloc[_plot_range]
        _px_colors = np.where(_plt_close>_plt_open, 'firebrick', 'darkslateblue')
        
        _tr = pxpddict['TurnoverRate'][_plot_ticker].iloc[_plot_range]
        
        try:
            axs.vlines(
                xs, 
                list(_plt_low.values), 
                list(_plt_high.values), 
                color=_px_colors,
                label=code_name_mapdict[_plot_ticker]['name'],
            )
        except:
            axs.vlines(
                    xs, 
                    list(_plt_low.values), 
                    list(_plt_high.values), 
                    color=_px_colors,
                )
        # plt.legend(loc=0, prop=fontP)
        axs.hlines(
            _plt_open, 
            np.array(xvs) - _ber_length, 
            xvs,
            color=_px_colors,
        )
        axs.hlines(
            _plt_close, 
            xvs, 
            np.array(xvs) + _ber_length,
            color=_px_colors,
        )
        
        try:
            axs.plot(xs, xpd_ma20[_plot_ticker].iloc[_plot_range].values, color='orange')
        #     axs.plot(xs, xpd_ma10[_plot_ticker].iloc[_plot_range].values, color='grey')
            axs.plot(xs, xpd_ma5[_plot_ticker].iloc[_plot_range].values, color='grey')
            
            axs.plot(xs, b_up[_plot_ticker].iloc[_plot_range].values, color='blue', alpha=0.5)
            axs.plot(xs, b_low[_plot_ticker].iloc[_plot_range].values, color='purple', alpha=0.5)
        except:
            pass

        if alertedindo is not None:
            # st.table(alertedindo[_plot_ticker].iloc[-len(xs):])
            # aids = [i for i in range(len(xs)) if alertedindo[_plot_ticker].iloc[-len(xs):].iloc[i]]
            _xs = [x for x in xs if int(x.replace("-", "")) in alertedindo.index]
            aids = [i for i in range(len(_xs)) if alertedindo[_plot_ticker].loc[int(_xs[i].replace("-", ""))]]
            # def _get_alert_state(x):
            #     try:
            #         if alertedindo.loc[int(x.replace("-", ""))][_plot_ticker]:
            #             return xs.index(x)
            #     except:
            #         pass
            # aids = [_get_alert_state(x) for x in xs]
            # st.write(aids)
            axs.scatter([xs[i] for i in aids], [pxpddict['Close'][_plot_ticker].iloc[_plot_range].iloc[i] for i in aids], c='red', alpha=0.5, s=100)

        axs_0 = axs.twinx()
        axs_0.vlines(obs_step, 0, 1, linestyles='--', colors='black')
        axs_0.vlines(len(xs) - obs_step, 0, 1, linestyles='--', colors='black')

        st.pyplot(fig, use_container_width=False)

        if savepath is not None:
            try:
                fig.savefig(f"{savepath}/{xxid}_{_plot_ticker}_{code_name_mapdict[_plot_ticker]['name']}.png", bbox_inches='tight')
            except:
                fig.savefig(f"{savepath}/{xxid}_{_plot_ticker}.png", bbox_inches='tight')
        
        fig, axs = plt.subplots(figsize=(16, 3))
        l1pd, l2pd, lhistpd = talib.MACD(xpd[_plot_ticker], fastperiod=12, slowperiod=26, signalperiod=9)
        axs.plot(xvs, l1pd.iloc[_plot_range], color='orange')
        axs.plot(xvs, l2pd.iloc[_plot_range], color='blue')
        axs.bar(xvs, lhistpd.iloc[_plot_range], color='blue')

        if savepath is not None:
            fig.savefig(f"{savepath}/{xxid}_{_plot_ticker}_macd.png", bbox_inches='tight')
        
        # if show:
            # plt.show()
        st.pyplot(fig, use_container_width=False)

        xxid+=1


def obs_names_at_specific_mth_streamlit_v2(_names=[], _ym="xxxx-xx",
                              xobj=None, 
                              code_name_mapdict=None,
                              xpd_ma20=None,
                              xpd_ma5=None,
                              b_low=None,
                              b_up=None,
                              xpd=None,
                              obs_step=20,
                              additional_info=[],
                              savepath=None,
                              show=True,
                              alertedindo=None
                              ):
# _names = ['603099',]
# _ym = '2024-01'
    histpx_d_qfq_axes = xobj['axes']
    pxpddict = xobj

    _dates = [x for x in histpx_d_qfq_axes['1str'] if _ym in x]
    _start_date_id = histpx_d_qfq_axes['1str'].index(_dates[0])
    _end_date_id = histpx_d_qfq_axes['1str'].index(_dates[-1])

    _plot_range = slice(_start_date_id-obs_step, _end_date_id+obs_step)
    _fig_size = (16, 5+2+2)
    _ber_length = 0.3


    xxid = 0
    for _plot_ticker in _names[:]:
        try:
            st.write(_plot_ticker, code_name_mapdict[_plot_ticker]['name'], end=";")
        except:
            pass
        if len(additional_info)>0:
            for adxsuit in additional_info:
                if type(adxsuit) in [list, tuple]:
                    if len(adxsuit)==2:
                        adx, _prefix = adxsuit
                        _suffix = ''
                    else:
                        adx, _prefix, _suffix = adxsuit
                else:
                    adx = adxsuit
                    _prefix, _suffix = '', ''
                try:
                    st.write(_prefix, adx[_plot_ticker], _suffix, end=";")
                except:
                    pass
        
        # _loc_id = histpx_d_qfq_axes[2].index(_plot_ticker)

        fig, axs = plt.subplots(nrows=3, ncols=1, height_ratios=[5, 2, 2], figsize=_fig_size, sharex=True, gridspec_kw=dict(hspace=0))
        # axs[0].plot(range(10), range(10))

        # fig, axs = plt.subplots(figsize=_fig_size)
        xs = [x.strftime("%Y-%m-%d") for x in histpx_d_qfq_axes[1][_plot_range]]
        xvs = range(len(xs))
        xticks = range(-len(xs), 0)
        axs[2].set_xticklabels(xticks)
        
        _plt_open = pxpddict['Open'][_plot_ticker].iloc[_plot_range]
        _plt_high = pxpddict['High'][_plot_ticker].iloc[_plot_range]
        _plt_low = pxpddict['Low'][_plot_ticker].iloc[_plot_range]
        _plt_close = pxpddict['Close'][_plot_ticker].iloc[_plot_range]
        _px_colors = np.where(_plt_close>_plt_open, 'firebrick', 'darkslateblue')
        
        _tr = pxpddict['TurnoverRate'][_plot_ticker].iloc[_plot_range]
        
        try:
            axs[0].vlines(
                xs, 
                list(_plt_low.values), 
                list(_plt_high.values), 
                color=_px_colors,
                label=code_name_mapdict[_plot_ticker]['name'],
            )
        except:
            axs[0].vlines(
                    xs, 
                    list(_plt_low.values), 
                    list(_plt_high.values), 
                    color=_px_colors,
                )
        # plt.legend(loc=0, prop=fontP)
        axs[0].hlines(
            _plt_open, 
            np.array(xvs) - _ber_length, 
            xvs,
            color=_px_colors,
        )
        axs[0].hlines(
            _plt_close, 
            xvs, 
            np.array(xvs) + _ber_length,
            color=_px_colors,
        )
        
        try:
            axs[0].plot(xs, xpd_ma20[_plot_ticker].iloc[_plot_range].values, color='orange')
        #     axs.plot(xs, xpd_ma10[_plot_ticker].iloc[_plot_range].values, color='grey')
            axs[0].plot(xs, xpd_ma5[_plot_ticker].iloc[_plot_range].values, color='grey')
            
            axs[0].plot(xs, b_up[_plot_ticker].iloc[_plot_range].values, color='blue', alpha=0.5)
            axs[0].plot(xs, b_low[_plot_ticker].iloc[_plot_range].values, color='purple', alpha=0.5)
        except:
            pass

        _plt_ema12 = pxpddict['Close'][_plot_ticker].ewm(span=12, adjust=False).mean()
        _plt_ema26 = pxpddict['Close'][_plot_ticker].ewm(span=26, adjust=False).mean()
        _plt_ema60 = pxpddict['Close'][_plot_ticker].ewm(span=60, adjust=False).mean()
        _plt_ema130 = pxpddict['Close'][_plot_ticker].ewm(span=130, adjust=False).mean()
        _plt_ema260 = pxpddict['Close'][_plot_ticker].ewm(span=260, adjust=False).mean()
        
        axs[0].plot(xvs, _plt_ema12.iloc[_plot_range], color='red', alpha=0.2)
        axs[0].plot(xvs, _plt_ema26.iloc[_plot_range], color='blue', alpha=0.2)
        axs[0].plot(xvs, _plt_ema60.iloc[_plot_range], color='orange', alpha=0.2)
        axs[0].plot(xvs, _plt_ema130.iloc[_plot_range], color='green', alpha=0.2)
        axs[0].plot(xvs, _plt_ema260.iloc[_plot_range], color='purple', alpha=0.2)

        if alertedindo is not None:
            # st.table(alertedindo[_plot_ticker].iloc[-len(xs):])
            # aids = [i for i in range(len(xs)) if alertedindo[_plot_ticker].iloc[-len(xs):].iloc[i]]
            _xs = [x for x in xs if int(x.replace("-", "")) in alertedindo.index]
            aids = [i for i in range(len(_xs)) if alertedindo[_plot_ticker].loc[int(_xs[i].replace("-", ""))]]
            # def _get_alert_state(x):
            #     try:
            #         if alertedindo.loc[int(x.replace("-", ""))][_plot_ticker]:
            #             return xs.index(x)
            #     except:
            #         pass
            # aids = [_get_alert_state(x) for x in xs]
            # st.write(aids)
            axs[0].scatter([xs[i] for i in aids], [pxpddict['Close'][_plot_ticker].iloc[_plot_range].iloc[i] for i in aids], c='red', alpha=0.5, s=100)

        axs_0 = axs[0].twinx()
        axs_0.vlines(obs_step, 0, 1, linestyles='--', colors='black')
        axs_0.vlines(len(xs) - obs_step, 0, 1, linestyles='--', colors='black')

        # st.pyplot(fig, use_container_width=False)

        # if savepath is not None:
        #     try:
        #         fig.savefig(f"{savepath}/{xxid}_{_plot_ticker}_{code_name_mapdict[_plot_ticker]['name']}.png", bbox_inches='tight')
        #     except:
        #         fig.savefig(f"{savepath}/{xxid}_{_plot_ticker}.png", bbox_inches='tight')
        
        _plt_volume = pxpddict['TurnoverRate'][_plot_ticker].iloc[_plot_range]
        _plt_pctchg = pxpddict['Close'][_plot_ticker].pct_change().iloc[_plot_range]
        volcolors = np.where(_plt_pctchg>0, 'red', 'green')
        axs[1].bar(xvs, _plt_volume, color=volcolors)


        # fig, axs = plt.subplots(figsize=(16, 3))
        l1pd, l2pd, lhistpd = talib.MACD(xpd[_plot_ticker], fastperiod=12, slowperiod=26, signalperiod=9)
        axs[2].plot(xvs, l1pd.iloc[_plot_range], color='orange')
        axs[2].plot(xvs, l2pd.iloc[_plot_range], color='blue')
        axs[2].bar(xvs, lhistpd.iloc[_plot_range], color='blue')


        

        # try:
        #     axs[3].vlines(
        #         xs, 
        #         list(_plt_low.values), 
        #         list(_plt_high.values), 
        #         color=_px_colors,
        #         label=code_name_mapdict[_plot_ticker]['name'],
        #     )
        # except:
        #     axs[3].vlines(
        #             xs, 
        #             list(_plt_low.values), 
        #             list(_plt_high.values), 
        #             color=_px_colors,
        #         )
        # # plt.legend(loc=0, prop=fontP)
        # axs[3].hlines(
        #     _plt_open, 
        #     np.array(xvs) - _ber_length, 
        #     xvs,
        #     color=_px_colors,
        # )
        # axs[3].hlines(
        #     _plt_close, 
        #     xvs, 
        #     np.array(xvs) + _ber_length,
        #     color=_px_colors,
        # )

        import pandas as pd
        pd.DataFrame().ewm(span=12, adjust=False)

        # if savepath is not None:
        #     fig.savefig(f"{savepath}/{xxid}_{_plot_ticker}_macd.png", bbox_inches='tight')
        
        # if show:
            # plt.show()
        st.pyplot(fig, use_container_width=False)

        xxid+=1