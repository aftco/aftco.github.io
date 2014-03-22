var BOX_SCORES_PANEL = $('\
<div class="box-scores-panel panel panel-default">\
  <div class="panel-heading">&nbsp;</div>\
  <table class="table"><tbody></tbody></table>\
</div>\
');

var BoxScoresManager = function(options){
  this._options = {};
  if (options !== undefined) this._options = options;
  if (this._options.numTopPanel === undefined) this._options.numTopPanel = 5;
  if (this._options.numTeamPanel === undefined) this._options.numTeamPanel = 10;

  this._jsonUrl = "/box_scores/";
  this._teams = [];
  this._boxScores = {};
  this._displayPanels = null;
};

BoxScoresManager.prototype = {
  _teamToJsonTeam: function(team) {
    var toReturn = team.toLowerCase();
    var find = ' ';
    var re = new RegExp(find, 'g');
    toReturn = toReturn.replace(re, '_');
    return toReturn;
  },

  addTeam: function(team) {
    this._teams.push(team);
    var self = this;
    $.ajax({
      url: self._jsonUrl + self._teamToJsonTeam(team) + ".json",
      dataType: "json",
      success: function(data) {
        self._boxScores[team] = data;
        self._doDisplayPanel(team);
      },
      error: function(jqXHR, textStatus, errorThrown) {
      }
    });
  },

  displayPanels: function(container) {
    this._displayPanels = $(container);
    for (var i=0; i<this._teams.length; i++) {
      var team = this._teams[i];
      this._doDisplayPanel(team);
    }
  },

  _doDisplayPanel: function(team) {
    if (this._displayPanels === null) return;

    var teamData = this._boxScores[team];

    var teamPanel = BOX_SCORES_PANEL.clone();
    this._displayPanels.append(teamPanel);
    $('.panel-heading', teamPanel).html(team);
    var tbody = $('tbody', teamPanel);

    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
    tbody.append('<tr><td>date</td><td>team</td><td>other team</td><td>score</td></tr>');
  }
};
