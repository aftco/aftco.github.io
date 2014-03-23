var BOX_SCORES_PANEL = $('\
<div class="col-md-6">\
  <div class="box-scores-panel panel panel-default">\
    <div class="panel-heading"><h4 class="title">&nbsp;</h4></div>\
    <table class="table table-condensed"><tbody></tbody></table>\
    <div class="panel-footer">&nbsp;<div class="pull-right"><a href="#">More...</a></div></div>\
  </div>\
</div>\
');

var BoxScoreFormatter = function() {
};

BoxScoreFormatter.prototype = {
  shortFormat: function(teamData, boxScore) {
    var homeText = teamData.teamShort + " " + boxScore.final[0].toString();
    var opponentText = boxScore.opponent + " " + boxScore.final[1].toString();
    if (boxScore.home) {
      return opponentText + " @ " + homeText;
    }

    return homeText + " @ " + opponentText;
  }
};

var BoxScoresManager = function(options){
  this._options = {};
  if (options !== undefined) this._options = options;
  if (this._options.numTopPanel === undefined) this._options.numTopPanel = 5;
  if (this._options.numTeamPanel === undefined) this._options.numTeamPanel = 5;

  this._jsonUrl = "/box_scores/";
  this._formatter = new BoxScoreFormatter();
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

  addTeam: function(team, teamCode, teamShort) {
    var teamPanel = this._addTeamPanel(team, teamCode);
    var teamData = {
      teamName: team,
      teamShort: teamShort,
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
    if (this._displayPanels === null) return null;

    var teamPanel = BOX_SCORES_PANEL.clone();
    teamPanel.attr('id', teamCode + "-panel");
    this._displayPanels.append(teamPanel);

    $('.title', teamPanel).html(team);
    return teamPanel;
  },

  _doDisplayPanel: function(teamData) {
    var tbody = $('tbody', teamData.teamPanel);

    for (var i=0; i<this._options.numTeamPanel; i++) {
      if (teamData.data === null || i >= teamData.data.length) break;
      var score = this._formatter.shortFormat(teamData, teamData.data[i]);
      tbody.append('<tr><td>' + score + '</td></tr>');
    }
  }
};
