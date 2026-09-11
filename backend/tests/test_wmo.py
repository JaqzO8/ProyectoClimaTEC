from app.domain.wmo import get_wmo_condition


def test_clear_sky_day_and_night():
    cond_day = get_wmo_condition(0, is_day=True)
    assert cond_day.code == 0
    assert cond_day.key == "clear"
    assert cond_day.label_es == "Despejado"
    assert cond_day.icon_key == "sun"

    cond_night = get_wmo_condition(0, is_day=False)
    assert cond_night.icon_key == "moon"


def test_partly_cloudy():
    cond = get_wmo_condition(2, is_day=True)
    assert cond.key == "partly_cloudy"
    assert cond.label_es == "Parcialmente nublado"
    assert cond.icon_key == "partly_cloudy_day"


def test_rain_and_thunderstorm():
    rain = get_wmo_condition(63, is_day=True)
    assert rain.label_es == "Lluvia moderada"

    storm = get_wmo_condition(95, is_day=True)
    assert storm.label_es == "Tormenta eléctrica"
    assert storm.icon_key == "thunderstorm"


def test_unknown_wmo_code():
    unknown = get_wmo_condition(999, is_day=True)
    assert unknown.code == 999
    assert unknown.key == "unknown"
    assert "999" in unknown.label_es
