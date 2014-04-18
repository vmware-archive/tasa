require 'spec_helper'

feature 'Application' do
  before do
    visit 'http://localhost:3000/'
  end

  scenario 'Bill searches for "Acrobatics"' do
    expect(page).to have_css('h1')

    page.fill_in(:query, with: 'Acrobatics')
    page.find('.query-input').native.send_keys(:return)

    expect(page).to have_content('Tweets from June 30 - July 31 of 2013')
    expect(page).to have_css('.rickshaw_graph')
    expect(page).to have_css('.drilldown ol')

    actual = page.evaluate_script <<-JS
      _.map(d3.select('.total-tweets .graph path').data()[0], function(point) {
        return {posted_date: Number(point.posted_date), y: point.y};
      });
    JS
    expected = [
      {posted_date: 1372575600000 - 25200000, y: 14},
      {posted_date: 1372662000000 - 25200000, y: 10},
      {posted_date: 1372834800000 - 25200000, y: 7},
      {posted_date: 1372921200000 - 25200000, y: 8},
      {posted_date: 1373007600000 - 25200000, y: 6},
      {posted_date: 1373094000000 - 25200000, y: 5},
      {posted_date: 1373180400000 - 25200000, y: 5},
      {posted_date: 1373266800000 - 25200000, y: 15},
      {posted_date: 1373353200000 - 25200000, y: 3},
      {posted_date: 1373439600000 - 25200000, y: 9},
      {posted_date: 1373612400000 - 25200000, y: 8},
      {posted_date: 1373698800000 - 25200000, y: 10},
      {posted_date: 1373785200000 - 25200000, y: 11},
      {posted_date: 1373871600000 - 25200000, y: 14},
      {posted_date: 1373958000000 - 25200000, y: 11},
      {posted_date: 1374044400000 - 25200000, y: 9},
      {posted_date: 1374130800000 - 25200000, y: 8},
      {posted_date: 1374217200000 - 25200000, y: 6},
      {posted_date: 1374303600000 - 25200000, y: 9},
      {posted_date: 1374390000000 - 25200000, y: 12},
      {posted_date: 1374476400000 - 25200000, y: 16},
      {posted_date: 1374562800000 - 25200000, y: 5},
      {posted_date: 1374649200000 - 25200000, y: 5},
      {posted_date: 1374735600000 - 25200000, y: 13},
      {posted_date: 1374822000000 - 25200000, y: 5},
      {posted_date: 1374908400000 - 25200000, y: 13},
      {posted_date: 1374994800000 - 25200000, y: 5},
      {posted_date: 1375081200000 - 25200000, y: 17},
      {posted_date: 1375167600000 - 25200000, y: 7},
      {posted_date: 1375254000000 - 25200000, y: 13}
    ].map(&:with_indifferent_access)
    expect(actual).to eq(expected)

    actual = page.all('.drilldown ol li').map do |node|
      {username: node.find('.username').text, text: node.find('.text').text}
    end
    expected = [
      {username: "say4life", text: "acolyte acrobat"},
      {username: "_blasianBOMB", text: "Flip it, acrobat."},
      {username: "KENSHI0504", text: "I like acrobat!!!"},
      {username: "Ash_UpsideDown", text: "Acrobatic makeup sex. 😂"},
      {username: "hunter_kingg", text: "Tobacco packin acrobat"},
      {username: "redbeanns", text: "@YayaRosman acrobatic water skiing!"},
      {username: "MubasherJ7", text: "That was a great acrobatic clearance"},
      {username: "madiharris514", text: "Future career: acrobats :) @H2_hannah9"},
      {username: "DuncanDoeNuts_", text: "Tobacco packing acrobat"},
      {username: "DjScratchez", text: "Flippen the work like an acrobat"},
      {username: "JustJame5", text: "Faculty, office working, acrobats"},
      {username: "KENSHI0504", text: "I like acrobat!!!"},
      {username: "specialistSHY", text: "@ned_cleo heeeoooool... acrobatic moves..."},
      {username: "HappyLikeSiao", text: "acrobatic diving > Junho!!!!!!! ♥♥"},
      {username: "chaisebanks", text: "@SpaceKid_K with that acrobatic cheese lol"},
      {username: "Kitkatkaye", text: "Acrobatic morning y'all! :-D"},
      {username: "CeliaO2", text: "Acrobat reader http://t.co/5zQUCsqXlO"},
      {username: "la1nenu", text: "Acrobatics at night http://t.co/E8u7q6ZYEg"},
      {username: "KutThroatDro", text: "Acrobat shit too many flips"},
      {username: "connor_blackmon", text: "RT @_cwade: Connors an acrobat wtf"}
    ]
    expect(actual).to eq(expected)

    actual = page.evaluate_script '$(".tag-cloud").text()'
    expected = "acrobaticfreeamazingfirstgreatfullgoodaerialprofessional#acrobaticrealmorechinesegayquietlastfinaloldmanycutelongbadcoolfabulousbetterhardmagicredexcellentnormalhotbestfunnyawesomenewnextlivingflippinghalfbakedsexylittlestupiddrunkenmuchsurelivebrutalsignificantownsuchexclusiveentertainingsonicbrilliantdevastatinghardworkingjumpydivingcharismaticsupersonichighflyinghispanicokempty29yearsafeaweinspiringperfectromanticniceexistentialverbalintellectualfuntraditionalinterestingattractivebusydirtyexceptionalfewtalentedleftprodeceasedupsideeasyasianawarehilariousslightdefensivedarnfuturefirsteveroffensivetightselflessautomaticfurther"
    expect(actual).to eq(expected)
  end
end