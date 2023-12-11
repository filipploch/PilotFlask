class CEM:

  form_content = '''{{ form.hidden_tag() }}
    <div class="container">
      <div class="row">
        <div class="col-lg-4">
          <div class="form-group">
            {{ form.team_a.label(class="form-label") }}
            {{ form.team_a(class="form-control") }}
          </div>
          <div class="form-group">
            {{ form.team_b.label(class="form-label") }}
            {{ form.team_b(class="form-control") }}
          </div>
        </div>
        <div class="col-lg-4">
          <div>
            {{ form.competitions.label(class="form-label") }}
            {{ form.competitions(class="form-control") }}
          </div>
          <div class="form-group">
            {{ form.division.label(class="form-label") }}
            {{ form.division(class="form-control") }}
          </div>
        </div>
        <div class="col-lg-4">
          <div>
              {{ form.stadium.label(class="form-label") }}
              {{ form.stadium(class="form-control") }}
          </div>
        <div class="col-lg-6">
          <div class="form-group">
            {{ form.match_length.label(class="form-label") }}
            {{ form.match_length(class="form-control", value="2400") }}
          </div>
        </div>
          <div class="col-lg-6">
              {{ form.date_time.label }}
  
              <div class="input-group date">
                  <input id="date_time" name="date_time" required="" type="text" value="" class="form-control">
              </div>
          </div>
        </div>
      </div>
      <div class="row">
          {{ form.is_actual.label }} {{ form.is_actual }}
      </div>
      <div class="row">
        <div class="col-lg-4">
          <div class="form-group">
  
            <div class="panel panel-default">
              <div class="panel-heading">{{ form.commentators.label(class="form-label") }}</div>
              <div class="panel-body">
                <select class="select" name="commentators" id="commentators" multiple>
                  {% for option in form.commentators.choices %}
                  <option value="{{ option[0] }}">{{ option[1] }} {{ option[2] }}</option>
                  {% endfor %}
                </select>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="form-group">
            <div class="panel panel-default">
              <div class="panel-heading">{{ form.cameramen.label(class="form-label") }}</div>
              <div class="panel-body">
                <select class="select" name="cameramen" id="cameramen" multiple>
                  {% for option in form.cameramen.choices %}
                  <option value="{{ option[0] }}">{{ option[1] }} {{ option[2] }}</option>
                  {% endfor %}
                </select>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="form-group">
            <div class="panel panel-default">
              <div class="panel-heading">{{ form.referees.label(class="form-label") }}</div>
              <div class="panel-body">
                <select class="select" name="referees" id="referees" multiple>
                  {% for option in form.referees.choices %}
                  <option value="{{ option[0] }}">{{ option[1] }} {{ option[2] }}</option>
                  {% endfor %}
                </select>
              </div>
            </div>
          </div>
        </div>
        <button type="submit" class="btn btn-primary">Zapisz</button>
      </div>
    </div>'''
