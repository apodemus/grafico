from matplotlib import ticker
from matplotlib import scale as mscale
from matplotlib.transforms import (blended_transform_factory as btf,
                                   Transform, IdentityTransform, ScaledTranslation)
from mpl_toolkits.axes_grid1.parasite_axes import SubplotHost

#from decor import expose

from grafico.formatters import *
from grafico.ticks import locator_factory, formatter_factory

#****************************************************************************************************
class ReciprocalTransform(Transform): 
    input_dims = 1 
    output_dims = 1 
    is_separable = False 
    has_inverse = True 

    def __init__(self, thresh=1e-6):
        Transform.__init__(self)
        self.thresh = thresh

    def transform_non_affine(self, x): 
        mask = abs(x) < self.thresh
        #x[mask] = np.ma.masked#self.thresh
        #if any(mask):
            #xm = np.ma.masked_where(mask, x)
            #return 1. / xm
        #else:
        return 1. / x   

    def inverted(self): 
        return ReciprocalTransform()


#****************************************************************************************************
class ReciprocalFormatter(InfiniteAwareness, TransFormatter):
    _transform = ReciprocalTransform()

#****************************************************************************************************
class ReciprocalScale(mscale.ScaleBase):
    '''
    Scales data in range (0, inf) using a reciprocal scale.

    The (inverse) scale function:
    1 / x
    '''
    name = 'reciprocal'

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, axis, **kwargs):
        """
        Any keyword arguments passed to ``set_xscale`` and
        ``set_yscale`` will be passed along to the scale's
        constructor.
        """
        mscale.ScaleBase.__init__(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_transform(self):
        """
        Override this method to return a new instance that does the
        actual transformation of the data.
        """
        return ReciprocalTransform()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def limit_range_for_scale(self, vmin, vmax, minpos):
        """
        Override to limit the bounds of the axis to the domain of the
        transform.  Unlike the autoscaling provided by the tick locators,
        this range limiting will always be adhered to, whether the axis 
        range is set manually, determined automatically or changed through 
        panning and zooming.
        """
        print( vmin, vmax )
        return min(vmin,1e9), min(vmax, 1e9)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #@print_args()
    def set_default_locators_and_formatters(self, axis):
        """
        Override to set up the locators and formatters to use with the
        scale.  This is only required if the scale requires custom 
        locators and formatters."""
        
        majloc = axis.major.locator
        #print( majloc )
        #MajLoc = type('Foo', (majloc.__class__,), 
        #              {'__call__' : lambda obj: self.get_transform().transform( majloc() )}  )
        #print(majloc.__class__)
        
        class TransMajLoc(majloc.__class__):
            def __call__(obj):
                s = super(TransMajLoc, obj).__call__()
                r = self.get_transform().transform( s ) 
                print( 's', s )
                print( 'r', r )
                return r
        
        #print( TransMajLoc )
        #print( TransMajLoc() )
        #print( TransMajLoc()() )
        #axis.set_major_locator( TransMajLoc() )
        #q = ticker.ScalarFormatter()
        #embed()
        #axis.set_major_formatter( q )


#mscale.register_scale( ReciprocalScale )


#****************************************************************************************************
class DualAxes(SubplotHost):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kws):
        
        #self.xtrans =  kws.pop( 'xtrans', IdentityTransform() )
        #self.ytrans =  kws.pop( 'ytrans', IdentityTransform() )
        self.aux_trans = kws.pop( 'aux_trans', btf(IdentityTransform(),
                                                   IdentityTransform() ) )
        #embed()
        SubplotHost.__init__(self, *args, **kws)   #self.__class__, self
        
        #Initialize the parasite axis
        self.parasite = self.twin(self.aux_trans) # ax2 is responsible for "top" axis and "right" axis
   
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup_ticks(self):
        
        #Tick setup for both axes
        minorTickSize = 8
        for ax in (self.xaxis, self.parasite.xaxis):
            ax.set_tick_params('both', tickdir='out')
            ax.set_tick_params('minor', labelsize=minorTickSize, pad=5)
        
        #Tick setup for parasite axes
        self.xaxis.tick_bottom()
        self.parasite.xaxis.tick_top()
        #ax.parasite.yaxis.set_ticklabels([])
        self.parasite.axis['right'].major_ticklabels.set_visible(False)
        #self.parasite.axis['left'].major_ticklabels.set_visible(False)
        #self.parasite.axis['bottom'].major_ticklabels.set_visible(False)
        
        self.set_locators()
        self.set_formatters()
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_locators(self):
        
        #Set the major tick locator
        #Use the major locator of the primary (bottom) xaxis to construct the parasite (top) xaxis locator
        #TransLocator = locator_factory( self.xaxis.get_major_locator(), 
        #                                self.aux_trans )
        #self.parasite.xaxis.set_major_locator( TransLocator() )
        
        #Set the minor tick locator
        mloc = self.xaxis.get_minor_locator()
        if isinstance(mloc, ticker.NullLocator):
            mloc = ticker.AutoMinorLocator(2)
            self.xaxis.set_minor_locator(mloc)
        
        #similarly for the minor locator
        #TransMinorLocator = locator_factory( self.xaxis.get_minor_locator(), 
        #                                     self.aux_trans )
        self.parasite.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))#TransMinorLocator() )
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_formatters(self):
    
        
        #Set the major tick formatter
        #majorFreqForm = MetricFormatter('Hz', precision=1)
        #MinorFormatter = formatter_factory( ticker.ScalarFormatter() )
        #minFreqForm = MinorFreqFormatter()
        
        
        
        #fax.set_minor_formatter( minFreqForm  )
        #fax.set_major_formatter( majorFreqForm )
        
        
        #Time axis
        #Set the minor tick formatter#
        MinorScalarFormatter = formatter_factory(
            ticker.ScalarFormatter(useOffset=False))
        msf = ticker.ScalarFormatter(useOffset=False) #MinorScalarFormatter()                  #instance 
        self.xaxis.set_minor_formatter(msf)
        self.parasite.xaxis.set_minor_formatter(MinorScalarFormatter())
    


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_xscale(self, value, **kw):
        super(DualAxes, self).set_xscale(value, **kw)
        self.parasite.set_xscale(value, **kw)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #def format_coord(self, x, y):
        #'''Return a format string formatting the *x*, *y*, *y'* coord'''
        #if x is None:
            #xs = '???'
        #else:
            #xs = self.format_xdata(x)
        
        #if y is None:
            #ys, yps = ['???']*2
        #else:
            #yp = self.aux_trans.inverted().transform((x,y))
            
            #ys, yps = map(self.format_ydata, (y, yp))
        
        #return 'x=%s y=%s y`=%s' % (xs, ys, yps)
    

#****************************************************************************************************       
class ResiDualAxes(DualAxes):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup_ticks(self):
        
        #Tick setup for both axes
        minorTickSize = 8
        for ax in (self.yaxis, self.parasite.yaxis):
            ax.set_tick_params('both', tickdir='out')
            ax.set_tick_params('minor', labelsize=minorTickSize, pad=5)
        
        #Tick setup for parasite axes
#         self.yaxis.tick_bottom()
#         self.parasite.xaxis.tick_top()
        #ax.parasite.yaxis.set_ticklabels([])
        self.parasite.axis['right'].major_ticklabels.set_visible(False)
        #self.parasite.axis['left'].major_ticklabels.set_visible(False)
        #self.parasite.axis['bottom'].major_ticklabels.set_visible(False)
        
        self.set_locators()
        self.set_formatters()


    
#****************************************************************************************************       
class TimePhaseDualAxes(DualAxes): #NOTE: might be better as a function?
    ''' '''
    def __init__(self, *args, **kws):
        ''' '''
        P = kws.pop('period')
        aux_trans = Affine2D().translate(0, 0).scale(P)
        kws['aux_trans'] = aux_trans
        
        DualAxes.__init__(self, *args, **kws)
    




#def sexa(t, pos=None):
    #h = t % 24
    #m = (h-int(h))*60
    #s = (m-int(m))*60
    #return '{:02,d}:{:02,d}:{:02,d}'.format(int(h),int(m),int(s))


##****************************************************************************************************       
#from matplotlib.ticker import FuncFormatter

#class SexaTimeDualAxes( DualAxes ):
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #def __init__(self, *args, **kw):
        
        #DualAxes.__init__( self, *args, **kw )
        
        #fmt = FuncFormatter(sexa)
        #self.parasite.xaxis.set_major_formatter(fmt)
        
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #def setup_ticks(self):
        #for label in self.parasite.get_xticklabels():
            #label.set_ha('left')
            #label.set_rotation(30)
            
            
            
            
            
#****************************************************************************************************       
import numpy as np
import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import AutoDateFormatter, AutoDateLocator
from matplotlib.transforms import Affine2D

#from IPython import embed
#****************************************************************************************************       
#class HackedDateLocator(AutoDateLocator):
    #'''AutoDateLocator borks on viewlim_to_dt'''
    #def viewlim_to_dt(self):
        ##embed()
        #vi = self.axis.get_view_interval()[None].T
        #xy = np.c_[vi, np.zeros_like(vi)]
        #vpi = self.axis.axes.transAux.inverted().transform(xy).T[0]
        #print( vi )
        #print( xy )
        #print(  num2date(vpi) )
        #return num2date(vpi)

#****************************************************************************************************       
class DateTimeDualAxes(DualAxes):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    scales = {'s' : 24*60*60,
              'm' : 24*60,
              'h' : 24,
              'd' : 1 }
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kw):
        tscale = kw.pop( 'timescale', 'd' )
        start = kw.pop( 'start', '1-1-1' )
        if isinstance(start, str):
            start = datetime.datetime(*map(int, start.split('-')))
        if isinstance(start, tuple):
            start= datetime.datetime(*start)
        
        xoff = date2num(start)
        scale = self.scales[tscale]
        
        aux_trans = Affine2D().translate(-xoff, 0).scale(scale)

        DualAxes.__init__(self, *args, aux_trans=aux_trans, **kw)
        
        self.cid = self.figure.canvas.mpl_connect('draw_event', self._on_draw)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_locators(self):
        self._loc = AutoDateLocator()
        self.parasite.xaxis.set_major_locator(self._loc)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_formatters(self):
        
        fmt = AutoDateFormatter(self._loc)
        fmt.scaled[1. / (24. * 60.)] = '%H:%M:%S'
    
        self.parasite.xaxis.set_major_formatter(fmt)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup_ticks(self):
        
        self.set_locators()
        self.set_formatters()
        
        self.parasite.yaxis.set_ticklabels([])
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rotate_labels(self):
        ticklabels = self.parasite.xaxis.get_majorticklabels()
        for label in ticklabels:
            #print( label )
            label.set_ha('left')
            label.set_rotation(30)
        
        return ticklabels
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _on_draw(self, event):
        #HACK! The rotate_labels borks if called before the figure is rendered. 
        # this method does the rotation upon the first cal to draw
        fig = self.figure
        canvas = fig.canvas
        
        self.rotate_labels()
        canvas.mpl_disconnect(self.cid)         #disconnect callback.
        
        canvas.draw()                           #redraw the figure
        #NOTE: this is slow, but better than the world of pain and death below
        #NOTE: another option might be to subclass the Text artist???
        #TODO: submit a bug report for this hack...
        
        #patch = fig.patch
        #for label in ticklabels:
            #bbox = label.get_window_extent()
            #canvas.restore_region(patch, bbox)
            ##label.set_visible(False)
            ##label.draw(self.figure._cachedRenderer)
            #canvas.blit(bbox)
            
            #label.set_visible(True)
            #canvas.blit(label.get_window_extent())
        
        #background = canvas.copy_from_bbox(fig.bbox)
        #canvas.restore_region(background)
        #self.rotate_labels()
        #canvas.restore_region(background)
        #canvas.blit(fig.bbox)
        
        #canvas.draw()
        #canvas.mpl_disconnect(self.cid)  #disconnect callback.
        
#****************************************************************************************************       

    



#****************************************************************************************************       
class TimeFreqDualAxes(SubplotHost):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kw):
    
        xax = kw.pop('xax', 'f')
        self.xtrans = ReciprocalTransform()
        #self._aux_trans = btf(ReciprocalTransform(), IdentityTransform())
        
        SubplotHost.__init__(self, *args, **kw)
        self.parasite = self.twin()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup_ticks(self):
        
        #Tick setup for both axes
        minorTickSize = 8
        for ax in (self.xaxis, self.parasite.xaxis):
            ax.set_tick_params('both', tickdir='out')
            ax.set_tick_params('minor', labelsize=minorTickSize, pad=0)
        
        #Tick setup for parasite axes
        self.xaxis.tick_bottom()
        self.parasite.xaxis.tick_top()
        self.parasite.axis['right'].major_ticklabels.set_visible(False)
        
        
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #def set_formatters(self):
            
        self.xaxis.set_minor_formatter(ticker.ScalarFormatter())
        
        self.parasite.xaxis.set_major_formatter(ReciprocalFormatter())
        self.parasite.xaxis.set_minor_formatter(ReciprocalFormatter())
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #def set_locators(self):
        #formatter_factory(AutoMinorLocator(n=5))
        self.xaxis.set_minor_locator(ticker.AutoMinorLocator(n=5))
        
        self.parasite.xaxis.set_minor_locator(ticker.AutoMinorLocator(n=5))
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def format_coord(self, x, y):
        
        p = self.xtrans.transform(x)
        #x = self.format_xdata(x)
        #p = self.format_xdata(p)
        #f = self.period_axis.get_major_formatter().format_data_short(x)
        y = self.format_ydata(y)
            
        return 'f = {:.6f}; p = {:.3f};\ty = {}'.format( x, p, y )
        #return 'f = {}; p = {};\ty = {}'.format( x, p, y )

#****************************************************************************************************       
class TimeFreqDualAxes2(DualAxes):
    #FIXME: TICKS BREAK WHEN RANGE SPANS 0
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kw):
        
        xax = kw.pop( 'xax', 'f' )
        self.xtrans = ReciprocalTransform()     #TODO: SEPARATING TRANSFORMS
        aux_trans = kw.pop('aux_trans', btf(ReciprocalTransform(),
                                            IdentityTransform()))
        
        DualAxes.__init__(self, *args, aux_trans=aux_trans, **kw) #self.__class__, self
    
        if xax.lower().startswith( 'f' ):
            self.frequency_axis, self.period_axis = self.xaxis, self.parasite.xaxis
        else:
            self.period_axis, self.frequency_axis = self.xaxis, self.parasite.xaxis
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setup_ticks(self):
        super().setup_ticks()
        self.parasite.axis['right'].major_ticklabels.set_visible(False)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_formatters(self):
    
        fax, pax = self.frequency_axis, self.period_axis
        
        #Frequeny axis
        #Set the major tick formatter
        majorFreqForm = MetricFormatter('Hz', precision=2)
        MinorFreqFormatter = ticker.ScalarFormatter
        #MinorFreqFormatter = formatter_factory( MetricFormatter('Hz', 
                                                                #precision=1, 
                                                                #uselabel=False) )
        
        minFreqForm = MinorFreqFormatter()
        
        fax.set_minor_formatter(minFreqForm)
        fax.set_major_formatter(majorFreqForm)
        
        
        #Period axis
        
        
        #Set the minor tick formatter#
        #class MajorPerFormatter(ticker.ScalarFormatter):
            ##def __call__(self, x, pos=None):
            
            #def set_locs(self, locs):
                ##print(locs)
                #'set the locations of the ticks'
                #locs = locs[~np.isinf(locs)]
                #super(MajorPerFormatter, self).set_locs(locs)
        
        
        

                
        
        #majloc = NonInfLoc()
        #pax.set_major_locator(majloc)
        
        majfmt = ticker.ScalarFormatter(useOffset=False) #MajorPerFormatter
        pax.set_major_formatter(majfmt)
            
        MinorScalarFormatter = formatter_factory( ticker.ScalarFormatter(useOffset=False) )
        #minfmt = MajorPerFormatter(useOffset=False)                    #instance # 
        minfmt = MinorScalarFormatter() 
        pax.set_minor_formatter(minfmt)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_locators(self):
        
                #class NonInfLoc(ticker.AutoLocator):
            
            #def tick_values(self, vmin, vmax):
                #return ticker.AutoLocator.tick_values(self, vmin, vmax)
                ##vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander=1e-13,
                                                                #tiny=1e-14)
                #print('tickvaalues', vmin, vmax)
                #locs = self.bin_boundaries(vmin, vmax)
                #prune = self._prune
                #if prune == 'lower':
                    #locs = locs[1:]
                #elif prune == 'upper':
                    #locs = locs[:-1]
                #elif prune == 'both':
                    #locs = locs[1:-1]
                #return self.raise_if_exceeds(locs)
        
        #Set the major tick locator
        #Use the major locator of the primary (bottom) xaxis to construct the parasite (top) xaxis locator
        TransLocator = locator_factory( self.xaxis.get_major_locator(), 
                                        self.xtrans )
        self.parasite.xaxis.set_major_locator( TransLocator() )
        
        #Set the minor tick locator
        mloc = self.xaxis.get_minor_locator()
        if isinstance(mloc, ticker.NullLocator):
            mloc = ticker.AutoMinorLocator()
            self.xaxis.set_minor_locator( mloc )
        
        #similarly for the minor locator
        TransMinorLocator = locator_factory( self.xaxis.get_minor_locator(), 
                                             self.xtrans )
        self.parasite.xaxis.set_minor_locator( TransMinorLocator() )
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def format_coord(self, x, y):
        
        p = self.xtrans.transform(x)
        #x = self.format_xdata(x)
        #p = self.format_xdata(p)
        #f = self.period_axis.get_major_formatter().format_data_short(x)
        y = self.format_ydata(y)
            
        return 'f = {:.6f}; p = {:.3f};\ty = {}'.format( x, p, y )
        #return 'f = {}; p = {};\ty = {}'.format( x, p, y )
                