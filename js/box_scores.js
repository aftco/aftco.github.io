var BOX_SCORES_PANEL = $('\
<div class="col-md-6">\
  <div class="box-scores-panel panel panel-default">\
    <div class="panel-heading"><h4 class="title">&nbsp;</h4></div>\
    <table class="table"><tbody></tbody></table>\
    <div class="panel-footer">&nbsp;<div class="pull-right"><a href="#">More...</a></div></div>\
  </div>\
</div>\
');

var BoxScoresManager = function(options){
  this._options = {};
  if (options !== undefined) this._options = options;
  if (this._options.numTopPanel === undefined) this._options.numTopPanel = 5;
  if (this._options.numTeamPanel === undefined) this._options.numTeamPanel = 5;

  this._jsonUrl = "/box_scores/";
  this._teams = {};
  this._displayPanels = null;
};

BoxScoresManager.prototype = {
  _teamToCode: function(team) {
    var toReturn = team.toLowerCase();
    var find = ' ';
    var re = new RegExp(find, 'g');
    toReturn = toReturn.replace(re, '_');
    return toReturn;
  },

  addTeam: function(team) {
    var teamCode = this._teamToCode(team);
    var teamPanel = this._addTeamPanel(team, teamCode);
    var teamData = {
      team: team,
      teamCode: teamCode,
      teamPanel: teamPanel,
      data: null
    };
    this._teams[team] = teamData;

    var self = this;
    $.ajax({
      url: self._jsonUrl + teamCode + ".json",
      dataType: "json",
      success: function(data) {
        teamData.data = data;
        self._doDisplayPanel(teamData);
      },
      error: function(jqXHR, textStatus, errorThrown) {
      }
    });
  },

  displayPanels: function(container) {
    this._displayPanels = $(container);
  },

  _addTeamPanel: function(team, teamCode) {
    if (this._displayPanels === null) return;

    var teamPanel = BOX_SCORES_PANEL.clone();
    this._displayPanels.append(teamPanel);

    $('.title', teamPanel).html(team);
    return teamPanel;
  },

  _doDisplayPanel: function(teamData) {
    var tbody = $('tbody', teamData.teamPanel);

    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
  }
};
