INSERT INTO Account (AccountID, Username, Password, Role, Name, Address, Phone) VALUES
(10001, 'johnlee', 'pass123', 'USER', 'John Lee', 'Teaching A', '61234567'),
(10002, 'annawang', 'pwanna', 'USER', 'Anna Wang', 'Harmonia College B', '61234568'),
(10003, 'michaelchan', 'mike321', 'USER', 'Michael Chan', 'Muse College D', '61234569'),
(10004, 'emilyzhang', 'ezpass', 'USER', 'Emily Zhang', 'Teaching C', '61234570'),
(10005, 'kevinli', 'kevin2025', 'USER', 'Kevin Li', 'Minerva College A', '61234571'),
(10006, 'saratan', 'saraabc', 'USER', 'Sara Tan', 'Library', '61234572'),
(10007, 'andrewho', 'andhoxx', 'USER', 'Andrew Ho', 'Ling College B', '61234573'),
(10008, 'natalielam', 'natpass', 'USER', 'Natalie Lam', 'Diligentia College C', '61234574'),
(10009, 'davidng', 'davidng', 'USER', 'David Ng', 'Teaching B', '61234575'),
(10010, 'janetcheung', 'janetpw', 'USER', 'Janet Cheung', 'Harmonia College A', '61234576'),
(10011, 'raymondchan', 'ray321', 'USER', 'Raymond Chan', 'Shaw College D', '61234577'),
(10012, 'vivianlau', 'vivpw', 'USER', 'Vivian Lau', 'Minerva College B', '61234578'),
(10013, 'peteryeung', 'petery', 'USER', 'Peter Yeung', 'Duan College A', '61234579'),
(10014, 'chloewong', 'chlow', 'USER', 'Chloe Wong', '8th College B', '61234580'),
(10015, 'thomasleung', 'thompw', 'USER', 'Thomas Leung', 'Ling College C', '61234581'),
(10016, 'angelachen', 'angpw', 'USER', 'Angela Chen', 'Teaching D', '61234582'),
(10017, 'justinlam', 'justpw', 'USER', 'Justin Lam', 'Diligentia College A', '61234583'),
(10018, 'rachelma', 'rachelpw', 'USER', 'Rachel Ma', 'Minerva College D', '61234584'),
(10019, 'brianho', 'bripass', 'USER', 'Brian Ho', 'Teaching A', '61234585'),
(10020, 'lucyzhang', 'lucyz', 'USER', 'Lucy Zhang', 'Muse College C', '61234586'),
(10021, 'calvinlee', 'calv321', 'USER', 'Calvin Lee', 'Duan College D', '61234587'),
(10022, 'stellaip', 'stpw', 'USER', 'Stella Ip', 'Ling College A', '61234588'),
(10023, 'henrylau', 'henpw', 'USER', 'Henry Lau', '8th College A', '61234589'),
(10024, 'amandacheng', 'amandapw', 'USER', 'Amanda Cheng', 'Shaw College B', '61234590'),
(10025, 'erictam', 'ericpw', 'USER', 'Eric Tam', 'Harmonia College D', '61234591'),
(10026, 'meganwong', 'meg321', 'USER', 'Megan Wong', 'Teaching C', '61234592'),
(10027, 'wilsonho', 'wilpw', 'USER', 'Wilson Ho', 'Duan College B', '61234593'),
(10028, 'evelynchow', 'evepw', 'USER', 'Evelyn Chow', 'Library', '61234594'),
(10029, 'victorlee', 'vicpw', 'USER', 'Victor Lee', 'Minerva College C', '61234595'),
(10030, 'angelayu', 'angpw', 'USER', 'Angela Yu', 'Diligentia College D', '61234596'),
(10031, 'oscarfung', 'oscpw', 'USER', 'Oscar Fung', '8th College C', '61234597'),
(10032, 'sophielin', 'sopw', 'USER', 'Sophie Lin', 'Muse College A', '61234598'),
(10033, 'nicholasho', 'nichpw', 'USER', 'Nicholas Ho', 'Ling College D', '61234599'),
(10034, 'carollai', 'carpw', 'USER', 'Carol Lai', 'Shaw College C', '61234600'),
(10035, 'ethanwan', 'ethpw', 'USER', 'Ethan Wan', 'Teaching B', '61234601'),
(10036, 'gracecheng', 'grapw', 'USER', 'Grace Cheng', 'Harmonia College C', '61234602'),
(10037, 'jasoncheung', 'jaspw', 'USER', 'Jason Cheung', 'Duan College C', '61234603'),
(10038, 'kellychan', 'kelpw', 'USER', 'Kelly Chan', '8th College D', '61234604'),
(10039, 'admin1', 'adminpass', 'ADMIN', 'System Admin', 'Teaching A', '61234605'),
(10040, 'admin2', 'rootpass', 'ADMIN', 'Database Admin', 'Library', '61234606');

INSERT INTO Store (StoreID, Name, Location) VALUES
(1, 'Shaw Canteen', 'Shaw College B 2nd Floor'),
(2, 'Happy Hour', 'Student Centre'),
(3, 'Haroma Cafeteria', 'Harmonia College Square'),
(4, 'Luna Marina', 'Muse College B'),
(5, 'Duan Family College Canteen', 'Duan College B1'),
(6, 'Lakeview Terrace', 'Conference Complex I 1st Floor'),
(7, 'School of Music Canteen', 'School of Music Entrance');

INSERT INTO Driver (DriverID, Name, Phone, IsActive) VALUES
(201, '王伟', '61239001', 1),
(202, '李娜', '61239002', 1),
(203, '张强', '61239003', 0),
(204, '刘洋', '61239004', 1),
(205, '陈晨', '61239005', 1),
(206, '林婷', '61239006', 0),
(207, '赵磊', '61239007', 1),
(208, '黄静', '61239008', 1),
(209, '周凯', '61239009', 1),
(210, '吴芳', '61239010', 0);

INSERT INTO MenuItem (MenuItemID, StoreID, Name, Price) VALUES
-- Shaw Canteen (StoreID = 1)
(1001, 1, 'Beef Noodle Soup', 26.0),
(1002, 1, 'Pork and Chive Dumplings (10 pcs)', 20.0),
(1003, 1, 'Braised Eggplant Bowl', 18.0),
(1004, 1, 'Kung Pao Chicken Bowl', 22.0),
(1005, 1, 'Scallion Oil Noodles', 19.0),
(1006, 1, 'Shredded Potato with Chili', 12.0),

-- Happy Hour (StoreID = 2)
(1007, 2, 'Hong Kong Style Egg Waffles', 16.0),
(1008, 2, 'Bacon and Egg Breakfast Plate', 25.0),
(1009, 2, 'Kimchi Fried Rice', 26.0),
(1010, 2, 'Korean Bibimbap', 32.0),
(1011, 2, 'Cheese Tteokbokki', 22.0),
(1012, 2, 'Honey Lemon Tea', 12.0),

-- Haroma Cafeteria (StoreID = 3)
(1013, 3, 'Grilled Salmon with Mashed Potatoes', 42.0),
(1014, 3, 'Beef Lasagna', 38.0),
(1015, 3, 'Classic Caesar Salad', 25.0),
(1016, 3, 'Chicken Alfredo Pasta', 36.0),
(1017, 3, 'Mushroom Soup with Garlic Bread', 18.0),
(1018, 3, 'Lemon Iced Tea', 14.0),

-- Luna Marina (StoreID = 4)
(1019, 4, 'Spicy Chicken Rice', 28.0),
(1020, 4, 'Pork and Cabbage Dumplings (10 pcs)', 20.0),
(1021, 4, 'Sweet and Sour Chicken', 30.0),
(1022, 4, 'Spicy Chicken Wings', 25.0),
(1023, 4, 'Handmade Wontons', 22.0),
(1024, 4, 'Iced Soy Milk', 8.0),

-- Duan Family College Canteen (StoreID = 5)
(1025, 5, 'Black Pepper Chicken Chop Rice', 28.0),
(1026, 5, 'Hainanese Chicken Rice', 32.0),
(1027, 5, 'Tom Yum Soup', 30.0),
(1028, 5, 'Vietnamese Spring Rolls', 24.0),
(1029, 5, 'Curry Beef Brisket Rice', 34.0),
(1030, 5, 'Mango Sticky Rice', 18.0),

-- Lakeview Terrace (StoreID = 6)
(1031, 6, 'BBQ Pork Rice Noodles', 20.0),
(1032, 6, 'Beef Rice Noodles', 22.0),
(1033, 6, 'Shrimp Wonton Noodles', 26.0),
(1034, 6, 'Guilin Rice Noodles', 24.0),
(1035, 6, 'Soup Dumplings (6 pcs)', 18.0),
(1036, 6, 'Soy Milk and Fried Dough Set', 15.0),

-- School of Music Canteen (StoreID = 7)
(1037, 7, 'Pan-Seared Duck Breast with Orange Glaze', 58.0),
(1038, 7, 'Truffle Cream Pasta', 55.0),
(1039, 7, 'Smoked Salmon Croissant', 42.0),
(1040, 7, 'Avocado Toast with Poached Egg', 36.0),
(1041, 7, 'Crème Brûlée', 28.0),
(1042, 7, 'Cappuccino', 20.0);
