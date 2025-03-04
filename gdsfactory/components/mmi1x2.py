from __future__ import annotations

import gdsfactory as gf
from gdsfactory.add_padding import get_padding_points
from gdsfactory.component import Component
from gdsfactory.components.straight import straight
from gdsfactory.components.taper import taper as taper_function
from gdsfactory.typings import ComponentSpec, CrossSectionSpec, Optional


@gf.cell
def mmi1x2(
    width: Optional[float] = None,
    width_taper: float = 1.0,
    length_taper: float = 10.0,
    length_mmi: float = 5.5,
    width_mmi: float = 2.5,
    gap_mmi: float = 0.25,
    taper: ComponentSpec = taper_function,
    with_bbox: bool = True,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    r"""Returns 1x2 MultiMode Interferometer (MMI).

    Args:
        width: input and output straight width.
        width_taper: interface between input straights and mmi region.
        length_taper: into the mmi region.
        length_mmi: in x direction.
        width_mmi: in y direction.
        gap_mmi:  gap between tapered wg.
        taper: taper function.
        straight: straight function.
        with_bbox: add rectangular box in cross_section
            bbox_layers and bbox_offsets to avoid DRC sharp edges.
        cross_section: specification (CrossSection, string or dict).


    .. code::

               length_mmi
                <------>
                ________
               |        |
               |         \__
               |          __  E1
            __/          /_ _ _ _
         W0 __          | _ _ _ _| gap_mmi
              \          \__
               |          __  E0
               |         /
               |________|

             <->
        length_taper

    """
    c = Component()
    gap_mmi = gf.snap.snap_to_grid(gap_mmi, nm=2)
    w_mmi = width_mmi
    w_taper = width_taper
    x = gf.get_cross_section(cross_section)
    width = width or x.width

    taper = gf.get_component(
        taper,
        length=length_taper,
        width1=width,
        width2=w_taper,
        cross_section=cross_section,
        add_pins=None,
        add_bbox=None,
        decorator=None,
    )

    a = gap_mmi / 2 + width_taper / 2
    mmi = c << gf.get_component(
        straight,
        length=length_mmi,
        width=w_mmi,
        cross_section=cross_section,
        add_pins=None,
        add_bbox=None,
        decorator=None,
    )

    ports = [
        gf.Port(
            "o1",
            orientation=180,
            center=(0, 0),
            width=w_taper,
            layer=x.layer,
            cross_section=x,
        ),
        gf.Port(
            "o2",
            orientation=0,
            center=(+length_mmi, +a),
            width=w_taper,
            layer=x.layer,
            cross_section=x,
        ),
        gf.Port(
            "o3",
            orientation=0,
            center=(+length_mmi, -a),
            width=w_taper,
            layer=x.layer,
            cross_section=x,
        ),
    ]

    for port in ports:
        taper_ref = c << taper
        taper_ref.connect(port="o2", destination=port)
        c.add_port(name=port.name, port=taper_ref.ports["o1"])
        c.absorb(taper_ref)

    if with_bbox:
        padding = []
        for offset in x.bbox_offsets:
            points = get_padding_points(
                component=c,
                default=0,
                bottom=offset,
                top=offset,
            )
            padding.append(points)

        for layer, points in zip(x.bbox_layers, padding):
            c.add_polygon(points, layer=layer)

    c.absorb(mmi)
    if x.add_bbox:
        c = x.add_bbox(c)
    if x.add_pins:
        c = x.add_pins(c)
    if x.decorator:
        c = x.decorator(c)
    return c


if __name__ == "__main__":
    import gdsfactory as gf

    c = gf.components.mmi1x2(cross_section="rib_conformal")

    # print(c.xmin)
    # c.xmin = 0
    # print(c.xmin)

    c.show(show_ports=True)
