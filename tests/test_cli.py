from __future__ import annotations

from lgdo import cli, lh5


def test_lh5ls(lgnd_test_data):
    cli.lh5ls(
        [
            "-a",
            lgnd_test_data.get_path("lh5/LDQTA_r117_20200110T105115Z_cal_geds_raw.lh5"),
            "geds/raw",
        ]
    )


def test_lh5concat(lgnd_test_data, tmptestdir):
    outfile = f"{tmptestdir}/out.lh5"
    cli.lh5concat(
        [
            "--output",
            outfile,
            "--",
            lgnd_test_data.get_path(
                "lh5/prod-ref-l200/generated/tier/raw/phy/p03/r001/l200-p03-r001-phy-20230322T160139Z-tier_raw.lh5"
            ),
            lgnd_test_data.get_path(
                "lh5/prod-ref-l200/generated/tier/raw/phy/p03/r001/l200-p03-r001-phy-20230322T170202Z-tier_raw.lh5"
            ),
        ]
    )

    assert lh5.ls(outfile) == [
        "ch1057600",
        "ch1059201",
        "ch1062405",
        "ch1084803",
        "ch1084804",
        "ch1121600",
    ]
    assert lh5.ls(outfile, "ch1057600/raw/") == [
        "ch1057600/raw/abs_delta_mu_usec",
        "ch1057600/raw/baseline",
        "ch1057600/raw/board_id",
        "ch1057600/raw/channel",
        "ch1057600/raw/crate",
        "ch1057600/raw/daqenergy",
        "ch1057600/raw/deadtime",
        "ch1057600/raw/delta_mu_usec",
        "ch1057600/raw/dr_maxticks",
        "ch1057600/raw/dr_start_pps",
        "ch1057600/raw/dr_start_ticks",
        "ch1057600/raw/dr_stop_pps",
        "ch1057600/raw/dr_stop_ticks",
        "ch1057600/raw/event_type",
        "ch1057600/raw/eventnumber",
        "ch1057600/raw/fc_input",
        "ch1057600/raw/fcid",
        "ch1057600/raw/mu_offset_sec",
        "ch1057600/raw/mu_offset_usec",
        "ch1057600/raw/numtraces",
        "ch1057600/raw/packet_id",
        "ch1057600/raw/runtime",
        "ch1057600/raw/slot",
        "ch1057600/raw/timestamp",
        "ch1057600/raw/to_master_sec",
        "ch1057600/raw/to_start_sec",
        "ch1057600/raw/to_start_usec",
        "ch1057600/raw/tracelist",
        "ch1057600/raw/ts_maxticks",
        "ch1057600/raw/ts_pps",
        "ch1057600/raw/ts_ticks",
        "ch1057600/raw/waveform",
    ]
    assert lh5.ls(outfile, "ch1057600/raw/waveform/") == [
        "ch1057600/raw/waveform/dt",
        "ch1057600/raw/waveform/t0",
        "ch1057600/raw/waveform/values",
    ]

    store = lh5.LH5Store()
    _, size = store.read("ch1057600/raw", outfile)
    assert size == 20

    arg_list = [
        "--overwrite",
        "--output",
        outfile,
        "--include",
        "ch1057600/raw/waveform/*",
        "--",
        lgnd_test_data.get_path(
            "lh5/prod-ref-l200/generated/tier/raw/phy/p03/r001/l200-p03-r001-phy-20230322T160139Z-tier_raw.lh5"
        ),
        lgnd_test_data.get_path(
            "lh5/prod-ref-l200/generated/tier/raw/phy/p03/r001/l200-p03-r001-phy-20230322T170202Z-tier_raw.lh5"
        ),
    ]

    cli.lh5concat(arg_list)
    assert lh5.ls(outfile) == [
        "ch1057600",
    ]

    arg_list[4] = "ch1057600/raw/waveform/values"
    cli.lh5concat(arg_list)
    assert lh5.ls(outfile, "ch1057600/raw/waveform/") == [
        "ch1057600/raw/waveform/values",
    ]

    arg_list[3] = "--exclude"
    arg_list[4] = "ch1057600/raw/waveform/values"
    cli.lh5concat(arg_list)
    assert lh5.ls(outfile) == [
        "ch1057600",
        "ch1059201",
        "ch1062405",
        "ch1084803",
        "ch1084804",
        "ch1121600",
    ]
    assert lh5.ls(outfile, "ch1057600/raw/waveform/") == [
        "ch1057600/raw/waveform/dt",
        "ch1057600/raw/waveform/t0",
    ]
