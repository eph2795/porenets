import openpnm.models as mods
from openpnm.geometry import GenericGeometry


class Imported(GenericGeometry):
    r"""
    This geometry class extracts all numerical properites from the received
    network object and moves them to itself.
    This class is mostly intended for use with networks imported from various
    network extraction codes, where the geometry properties are included on
    the network itself.  In these cases, an error occurs when adding other
    geometries to the project, such as adding boundary pores or in more
    elaborate scenarios such as stitching networks together.  The issue is
    that OpenPNM prevent a property, such as 'pore.volume', from exiting on
    both the network and also a geometry.  Thus it is necessary to move the
    extracted network properties to this ``Imported`` class, then creating
    new geometry objects for any added pores.
    Parameters
    ----------
    network : OpenPNM Network object
        The network with which this Geometry should be associated
    exclude : list of strings
        A list of which network properties should *not* be transferred to
        new geometry object.  'pore.coords' and 'throat.conns' are *always*
        excluded.  Note that labels are not transferred, only properties.
    project : OpenPNM Project object, optional
        Can be supplied instead in addition to ``network`` but is inferred
        from the network's project if not given.
    name : string
        The name of the object, which is also used as the label where this
        geometry is defined.
    """

    def __init__(self, network, exclude=[], **kwargs):
        super().__init__(network=network, **kwargs)
        exclude.extend(['pore.coords', 'throat.conns'])
        for item in network.props():
            if item not in exclude:
                self[item] = network.pop(item)

        if 'throat.endpoints' not in self.keys():
            self.add_model(propname='throat.endpoints',
                           model=mods.geometry.throat_endpoints.spherical_pores,
                           pore_diameter='pore.diameter',
                           throat_diameter='throat.diameter')

        if 'throat.length' not in self.keys():
            self.add_model(propname='throat.length',
                           model=mods.geometry.throat_length.piecewise,
                           throat_endpoints='throat.endpoints')

        self.add_model(propname='throat.conduit_lengths',
                       model=mods.geometry.throat_length.conduit_lengths,
                       throat_endpoints='throat.endpoints',
                       throat_length='throat.length')
