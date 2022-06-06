from select import select
from unicodedata import category
from flask import Blueprint, Flask, flash, jsonify, redirect, render_template, request, jsonify, url_for
from flask_login import login_required, current_user
from .models import Info, User
from . import db


views = Blueprint('views', __name__)

# !home page


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

# !path data-selection page


@views.route('/database')
@login_required
def dataSelectionPath():
    return render_template("data_path_selection.html", user=current_user)


# !record table page


@views.route('/sector_table/', methods=['GET', 'POST'])
@login_required
def databaseTable():
    all_data = Info.query.all()
    return render_template('sector_table.html', user=current_user, all_data=all_data)


# !update record page


@ views.route('/update_data/<int:id>', methods=['GET', 'POST'])
@ login_required
def update_data(id):
    data = Info.query.get_or_404(id)
    if request.method == 'POST':
        # *from form
        sector_name = request.form.get('sectorName')
        sector_type = request.form.get('sectorType')
        population = float(request.form.get('population'))
        housing = float(request.form.get('housing'))
        income = request.form.get('income')
        amount_waste = float(request.form.get('amountWaste'))
        edit_date = request.form.get('editDate')
        # *from calculation
        amount_waste_kg = amount_waste*1000
        housingSize_result = population/housing
        wasteRate_result = amount_waste*1000/population

        data.sector_name = sector_name
        data.sector_type = sector_type
        data.population = population
        data.housing = housing
        data.income = income
        data.amount_waste = amount_waste
        data.edit_date = edit_date
        data.amount_waste_kg = amount_waste_kg
        data.housing_size = housingSize_result
        data.waste_rate = wasteRate_result

        db.session.add(data)
        db.session.commit()

        flash(
            f'ข้อมูลของ {sector_name} บนฐานข้อมูลถูกแก้ไข้แล้ว', category='success')
        return redirect(url_for('views.home'))
        # try:
        #     db.session.add()
        #     db.session.commit()
        #     flash(
        #         f'ข้อมูลของ {sector_name} บนฐานข้อมูลถูกแก้ไข้แล้ว', category='success')
        #     return redirect(url_for('views.home'))
        # except:
        #     flash(
        #         f'ข้อมูลของ {sector_name} แก้ไขไม่สำเร็จ', category='error')
        #     return render_template('update_date.html', user=current_user, data=data)
    return render_template('update_data.html', user=current_user, data=data)


# !create new data page


@views.route('/create_data', methods=['GET', 'POST'])
@login_required
def createData():
    if request.method == 'POST':
        # *from form
        zone = request.form.get('zone')
        sector_name = request.form.get('sectorName')
        sector_type = request.form.get('sectorType')
        lat = request.form.get('lat')
        lng = request.form.get('long')
        address = request.form.get('address')
        population = request.form.get('population')
        housing = request.form.get('housing')
        income = request.form.get('income')
        amount_waste = request.form.get('amountWaste')
        edit_date = request.form.get('editDate')
        # housing_size = request.form.get('housingSize')
        # waste_rate = request.form.get('wasteRate')

        sector = Info.query.filter_by(sector_name=sector_name).first()
        if sector:
            flash(f'ข้อมูลของ {sector_name} มีบนฐานข้อมูลแล้ว',
                  category='error')
        elif zone is None:
            flash('กรุณาระบุภาค', category='error')
        elif len(sector) < 1:
            flash('กรุณาระบุชื่อองค์กรบริหารส่วนท้องถิ่น', category='error')
        elif sector is None:
            flash('กรุณาระบุประเภทขององค์กรบริหารส่วนท้องถิ่น', category='error')
        elif lat is None:
            flash('กรุณาระบุพิกัดละติจูด', category='error')
        elif lng is None:
            flash('กรุณาระบุพิกัดลองติจูด', category='error')
        elif address is None:
            flash('กรุณาระบุที่อยู่', category='error')
        elif population < 1:
            flash('กรุณาระบจำนวนประชากร', category='error')
        elif housing < 1:
            flash('กรุณาระบจำนวนครัวเรือน', category='error')
        elif len(edit_date) < 1:
            flash('กรุณาระบุวันที่ทำการแก้ไขข้อมูล', category='error')
        else:
            # *from calculation
            amount_waste_kg = float(amount_waste)*1000
            housingSize_result = float(population)/float(housing)
            wasteRate_result = float(amount_waste)*1000/float(population)
            data = Info(zone=zone,
                        sector_name=sector_name,
                        sector_type=sector_type,
                        lat=lat,
                        long=lng,
                        address=address,
                        population=population,
                        housing=housing,
                        income=income,
                        housing_size=housingSize_result,
                        amount_waste=amount_waste,
                        amount_waste_kg=amount_waste_kg,
                        waste_rate=wasteRate_result,
                        edit_date=edit_date,
                        user_id=current_user.id,
                        )
            db.session.add(data)
            db.session.commit()
            flash(f'ข้อมูลของ {sector_name} ถูกเพิ่มบนฐานข้อมูลแล้ว',
                  category='success')
            return redirect(url_for('views.home'))
    return render_template("create_data.html", user=current_user)
